"""
.. module: dispatch.plugins.dispatch_github.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import platform
import re
from re import Pattern
import sys
import requests
from datetime import datetime
from tenacity import TryAgain, retry, stop_after_attempt, wait_fixed

from . import __version__
from dispatch.config import BaseConfigurationModel
from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_github as github_plugin
from dispatch.plugins.bases.monitor import MonitorPlugin


class GithubConfiguration(BaseConfigurationModel):
    pass


def create_ua_string():
    client_name = __name__.split(".")[0]
    client_version = __version__  # Version is returned from _version.py

    # Collect the package info, Python version and OS version.
    package_info = {
        "client": "{0}/{1}".format(client_name, client_version),
        "python": "Python/{v.major}.{v.minor}.{v.micro}".format(v=sys.version_info),
        "system": "{0}/{1}".format(platform.system(), platform.release()),
    }

    # Concatenate and format the user-agent string to be passed into request headers
    ua_string = []
    for _, val in package_info.items():
        ua_string.append(val)

    return " ".join(ua_string)


# NOTE we don't yet support enterprise github
@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class GithubMonitorPlugin(MonitorPlugin):
    title = "Github Plugin - Github Monitoring"
    slug = "github-monitor"
    description = "Allows for the monitoring of Github issues and PRs."
    version = github_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = GithubConfiguration

    def get_matchers(self, *args, **kwargs) -> list[Pattern]:
        """Returns a list of regexes that this monitor plugin should look for in chat messages."""
        matchers = [
            r"(?P<weblink>https:\/\/github.com\/(?P<organization>[a-zA-Z0-9-_]+)*\/(?P<repo>[a-zA-Z0-9-_]+)*\/(?P<type>pull|issues)*\/(?P<id>\w+)*)"
        ]
        return [re.compile(r) for r in matchers]

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_match_status(self, weblink: str, last_modified: datetime = None, **kwargs) -> dict:
        """Fetches the match and attempts to determine current status."""
        # determine what kind of link we have
        base_url = "https://api.github.com/repos"

        # NOTE I'm not sure about this logic
        match_data = None
        for matcher in self.get_matchers():
            for match in matcher.finditer(f"<{weblink}>"):
                match_data = match.groupdict()
                if match_data:
                    break

        if match_data["type"] == "pull":
            # for some reason the api and the front end differ for PRs
            match_data["type"] = match_data["type"].replace("pull", "pulls")

        request_url = f"{base_url}/{match_data['organization']}/{match_data['repo']}/{match_data['type']}/{match_data['id']}"

        # use conditional requests to avoid rate limits
        # https://docs.github.com/en/rest/overview/resources-in-the-rest-api#conditional-requests
        headers = {"User-Agent": create_ua_string()}
        if last_modified:
            headers.update({"If-Modified-Since": str(last_modified)})

        resp = requests.get(request_url, headers=headers)

        if resp.status_code == 304:
            # no updates
            return

        if resp.status_code == 403:
            raise TryAgain

        if resp.status_code == 200:
            data = resp.json()
            monitor_data = {
                "title": data["title"],
                "state": data["state"],
            }

            return monitor_data
