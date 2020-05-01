"""
.. module: dispatch.plugins.dispatch_google_docs.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import unicodedata
from typing import Any, List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import DocumentPlugin
from dispatch.plugins.dispatch_google import docs as google_docs_plugin
from dispatch.plugins.dispatch_google.common import get_service


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


def insert_into_table(
    client: Any, document_id: str, table_index: int, cell_index: int, rows: List[dict]
):
    """Inserts rows and text into a table in an existing document."""
    # We insert as many rows as we need using the insertTableRow object.
    requests = []
    for _ in range(0, len(rows) - 1):
        requests.append(
            {
                "insertTableRow": {
                    "tableCellLocation": {
                        "tableStartLocation": {"index": table_index},
                        "rowIndex": 1,
                        "columnIndex": 1,
                    },
                    "insertBelow": "true",
                }
            }
        )

    # We insert the text into the table cells using the insertText object.
    index = cell_index  # set index to first empty cell
    for row in rows:
        for _, value in row.items():
            requests.append({"insertText": {"location": {"index": index}, "text": str(value)}})
            index += len(str(value)) + 2  # set index to next cell
        index += 1  # set index to new row

    body = {"requests": requests}
    return client.batchUpdate(documentId=document_id, body=body).execute()


def insert_incident_data(client: Any, document_id: str, index: int, incident_data: List[dict]):
    """Inserts incident data in an existing document."""
    requests = []
    for data in incident_data:
        key = data["key"]
        title = data["title"]
        summary = remove_control_characters(data["summary"])
        requests.append({"insertText": {"location": {"index": index}, "text": f"{key}: {title}\n"}})
        requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": index, "endIndex": index + len(f"{key}: {title}")},
                    "textStyle": {"bold": True},
                    "fields": "bold",
                }
            }
        )
        index += len(f"{key}: {title}\n")
        requests.append({"insertText": {"location": {"index": index}, "text": f"{summary}\n\n"}})
        index += len(f"{summary}\n\n")

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
        self.scopes = [
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive",
        ]

    def update(self, document_id: str, **kwargs):
        """Replaces text in document."""
        # TODO escape and use f strings? (kglisson)
        kwargs = {"{{" + k + "}}": v for k, v in kwargs.items()}
        client = get_service("docs", "v1", self.scopes).documents()
        return replace_text(client, document_id, kwargs)
