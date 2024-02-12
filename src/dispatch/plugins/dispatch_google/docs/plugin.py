"""
.. module: dispatch.plugins.dispatch_google_docs.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""

import logging
from typing import Any
from collections.abc import Generator
import unicodedata

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import DocumentPlugin
from dispatch.plugins.dispatch_google import docs as google_docs_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import GoogleConfiguration


log = logging.getLogger(__name__)


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


def find_links(obj: dict, find_key: str) -> iter(list[Any]):
    """Enumerate all the links found.
    Returns a path of object, from leaf to parents to root.

    Parameters:
        obj (dict): The object to search for links.
        find_key (str): The key to search for.

    Returns:
        iter: The generator of a list containing the value and the path to the value.

    This method was originally implemented in the open source library `Beancount`.
    The original source code can be found at
    https://github.com/beancount/beancount/blob/master/tools/transform_links_in_docs.py.
    BeanCount is licensed under the GNU GPLv2.0 license.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == find_key:
                yield [value, obj]
            else:
                for found in find_links(value, find_key):
                    found.append(obj)
                    yield found
    elif isinstance(obj, list):
        for value in obj:
            for found in find_links(value, find_key):
                found.append(obj)
                yield found


def iter_links(document_content: list) -> Generator[list[tuple[str, str]], None, None]:
    """Find all the links and return them.
    Parameters:
        document_content (list): The contents of the body of a Google Doc (googleapi.discovery.Resource).

    Returns:
        list: A list of tuples containing the hyperlink url (str) and its corresponding hyperlink element (str).
        e.g. [('https://www.netflix.com', {...{"textRun": {"textStyle": {"link": {"url": "https://www.netflix.com"}}}}})]

    See https://developers.google.com/docs/api/samples/output-json.

    This method was originally implemented in the open source library `Beancount`.
    The original source code can be found at
    https://github.com/beancount/beancount/blob/master/tools/transform_links_in_docs.py.
    BeanCount is licensed under the GNU GPLv2.0 license.
    """
    for jpath in find_links(document_content, "link"):
        for item in jpath:
            if "textRun" in item:
                link = item["textRun"]["textStyle"]["link"]
                if "url" not in link:
                    continue
                url = link["url"]
                yield (url, item)


def replace_weblinks(client: Resource, document_id: str, replacements: list[str]) -> int:
    """Replaces hyperlinks in specified document.

    If the url contains a placeholder, it will be replaced with the value in the replacements list.

    Parameters:
        client (Resource): The Google API client.
        document_id (str): The document id.
        replacements (list[str]): A list of string replacements to make.

    Returns:
        int: The number of hyperlink update requests made.
    """
    document = client.get(documentId=document_id).execute()

    if not document:
        log.warning(f"Document with id {document_id} not found.")
        return

    document_content = document.get("body").get("content")
    requests = []

    for url, item in iter_links(document_content):
        for k, v in replacements.items():
            if k in url and v:
                requests.append(
                    {
                        "updateTextStyle": {
                            "range": {
                                "startIndex": item["startIndex"],
                                "endIndex": (item["endIndex"]),
                            },
                            "textStyle": {"link": {"url": url.replace(k, v)}},
                            "fields": "link",
                        }
                    }
                )

    if not requests:
        return 0

    body = {"requests": requests}
    client.batchUpdate(documentId=document_id, body=body).execute()

    return len(requests)


def replace_text(client: Resource, document_id: str, replacements: list[str]) -> int:
    """Replaces text in specified document.

    Parameters:
        client (Resource): The Google API client.
        document_id (str): The document id.
        replacements (list[str]): A list of string replacements to make.

    Returns:
        int: The number of replacement requests made.
    """
    requests = []
    for k, v in replacements.items():
        requests.append(
            {"replaceAllText": {"containsText": {"text": k, "matchCase": "true"}, "replaceText": v}}
        )
    body = {"requests": requests}
    client.batchUpdate(documentId=document_id, body=body).execute()

    return len(requests)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleDocsDocumentPlugin(DocumentPlugin):
    title = "Google Docs Plugin - Document Management"
    slug = "google-docs-document"
    description = "Uses Google docs to manage document contents."
    version = google_docs_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = GoogleConfiguration
        self.scopes = [
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive",
        ]

    def update(self, document_id: str, **kwargs) -> None:
        """Replaces text in document."""
        # TODO escape and use f strings? (kglisson)
        kwargs = {"{{" + k + "}}": v for k, v in kwargs.items()}
        client = get_service(self.configuration, "docs", "v1", self.scopes).documents()
        replace_weblinks(client, document_id, kwargs)
        replace_text(client, document_id, kwargs)

    def insert(self, document_id: str, request) -> bool | None:
        client = get_service(self.configuration, "docs", "v1", self.scopes).documents()
        body = {"requests": request}
        try:
            response = client.batchUpdate(documentId=document_id, body=body).execute()
            if "replies" in response and response["replies"]:
                return True

        except HttpError as error:
            log.exception(error)
            return False
        except Exception as e:
            log.exception(e)
            return False

    def get_table_details(self, document_id: str, header: str) -> tuple[bool, int, int, list[int]]:
        client = get_service(self.configuration, "docs", "v1", self.scopes).documents()
        try:
            document_content = (
                client.get(documentId=document_id).execute().get("body").get("content")
            )
            start_index = 0
            end_index = 0
            header_index = 0
            past_header = False
            header_section = False
            table_exists = False
            table_indices = []
            headingId = ""
            for element in document_content:
                if "paragraph" in element and "elements" in element["paragraph"]:
                    for item in element["paragraph"]["elements"]:
                        if "textRun" in item:
                            if item["textRun"]["content"].strip() == header:
                                header_index = element["endIndex"]
                                header_section = True
                                headingId = element["paragraph"].get("paragraphStyle")["headingId"]

                            elif header_section:
                                # Gets the end index of any text below the header
                                if header_section and item["textRun"]["content"].strip():
                                    header_index = item["endIndex"]
                                # checking if we are past header in question
                                if (
                                    any(
                                        "headingId" in style
                                        for style in element["paragraph"]["paragraphStyle"]
                                        for style in element["paragraph"].get("paragraphStyle", {})
                                    )
                                    and element["paragraph"].get("paragraphStyle")["headingId"]
                                    != headingId
                                ):
                                    past_header = True
                                    header_section = False
                                    break
                # Checking for table under the header
                elif header_section and "table" in element and not past_header:
                    table_exists = True
                    start_index = element["startIndex"]
                    end_index = element["endIndex"]
                    table = element["table"]
                    for row in table["tableRows"]:
                        for cell in row["tableCells"]:
                            table_indices.append(cell["content"][0]["startIndex"])
                    return table_exists, start_index, end_index, table_indices
        except HttpError as error:
            log.exception(error)
            return table_exists, header_index, -1, table_indices
        except Exception as e:
            log.exception(e)
            return table_exists, header_index, -1, table_indices
        return table_exists, header_index, -1, table_indices

    def delete_table(self, document_id: str, request) -> bool | None:
        try:
            client = get_service(self.configuration, "docs", "v1", self.scopes).documents()
            body = {"requests": request}
            response = client.batchUpdate(documentId=document_id, body=body).execute()
            if "replies" in response and response["replies"]:
                return True

        except HttpError as error:
            log.exception(error)
            return False
        except Exception as e:
            log.exception(e)
            return False
