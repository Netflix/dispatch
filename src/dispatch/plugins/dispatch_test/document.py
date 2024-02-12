from dispatch.plugins.bases import DocumentPlugin
from googleapiclient.discovery import Resource
from googleapiclient.http import HttpRequestMock, BatchHttpRequest
from httplib2 import Response

_DOCUMENT_SUCCESS = {
    "body": {
        "content": [
            {
                "startIndex": 0,
                "endIndex": 40,
                "paragraph": {
                    "elements": [
                        {
                            "endIndex": 40,
                            "startIndex": 0,
                            "textRun": {
                                "content": "Incident Conversation Commands Reference",
                                "textStyle": {
                                    "link": {"url": "https://www.netflix.com/login"},
                                },
                            },
                        }
                    ],
                },
            },
        ]
    }
}

_DOCUMENT_FAIL = {"body": {"content": []}}


class TestResource(Resource):
    """A mock Google API Client"""

    def __init__(self, has_link: bool = True):
        self.has_link = has_link

    def batchUpdate(self, **kwargs) -> BatchHttpRequest:
        """Performs one or more update API requests."""
        return BatchHttpRequest(
            callback=None,
            batch_uri=None,
        )

    def get(self, documentId: int) -> HttpRequestMock:
        """Returns a mock HTTP request to fetch a document."""
        document = _DOCUMENT_SUCCESS if self.has_link else _DOCUMENT_FAIL

        return HttpRequestMock(
            resp=Response({"status": 200}),
            content="",
            postproc=lambda _x, _y: document,
        )


class TestDocumentPlugin(DocumentPlugin):
    title = "Dispatch Test Plugin - Document"
    slug = "test-document"

    def get(self, key, **kwargs):
        return

    def create(self, key, **kwargs):
        return

    def update(self, key, **kwargs):
        return

    def delete(self, key, **kwargs):
        return

    def move(self, key, **kwargs):
        return
