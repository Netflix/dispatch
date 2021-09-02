"""
.. module: dispatch.plugins.dispatch_github.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import re
import requests
from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_github as github_plugin
from dispatch.plugins.bases.monitor import MonitorPlugin


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

    def get_matchers():
        """Returns a list of regexes that this monitor plugin should look for in chat messages."""
        matchers = [
            r"^((https):\/)?\/?(?P<domain>[^:\/\s]+)(?P<repo>(?P<type>\/\w+)*\/)(?P<id>[\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$"
        ]
        return [re.compile(r) for r in matchers]

    def get_match_status(match_data) -> dict:
        """Fetches the match and attempts to determine current status."""
        # determine what kind of link we have
        base_url = "https://api.github.com/repos"

        if match_data["type"] == "/pull":
            # for some reason the api and the front end differ for PRs
            repo = match_data["repo"].replace("pull", "pulls")
            request_url = f"{base_url}/{repo}/{match_data['id']}"
            status_data = requests.get(request_url).json()

            # we pull out only the attributes we care about diff/monitor
            monitor_data = {
                "title": status_data["title"],
                "state": status_data["state"],
            }
            return monitor_data

        elif match_data["type"] == "/issues":
            request_url = f"{base_url}/{match_data['repo']}/{match_data['id']}"
            status_data = requests.get(request_url(request_url)).json()

            monitor_data = {
                "title": status_data["title"],
                "state": status_data["state"],
            }
            return monitor_data
