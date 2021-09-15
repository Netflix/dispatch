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
from dispatch.plugins.dispatch_google.config import GoogleConfiguration


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
