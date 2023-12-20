"""
.. module: dispatch.plugins.dispatch_google_docs.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import unicodedata
import logging
from typing import Any, List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import DocumentPlugin
from dispatch.plugins.dispatch_google import docs as google_docs_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import GoogleConfiguration
from googleapiclient.errors import HttpError

log = logging.getLogger(__name__)


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


def replace_text(client: Any, document_id: str, replacements: List[str]):
    """Replaces text in specified document."""
    requests = []
    for k, v in replacements.items():
        requests.append(
            {"replaceAllText": {"containsText": {"text": k, "matchCase": "true"}, "replaceText": v}}
        )
    body = {"requests": requests}
    return client.batchUpdate(documentId=document_id, body=body).execute()


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

    def update(self, document_id: str, **kwargs):
        """Replaces text in document."""
        # TODO escape and use f strings? (kglisson)
        kwargs = {"{{" + k + "}}": v for k, v in kwargs.items()}
        client = get_service(self.configuration, "docs", "v1", self.scopes).documents()
        return replace_text(client, document_id, kwargs)

    def insert(self, document_id: str, request):
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

    def get_table_details(self, document_id: str, header: str):
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

    def delete_table(self, document_id: str, request):
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
