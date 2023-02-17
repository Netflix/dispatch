from dispatch.plugins.dispatch_atlassian_confluence import docs as confluence_doc_plugin
from dispatch.plugins.bases import DocumentPlugin
from dispatch.plugins.dispatch_atlassian_confluence.config import ConfluenceConfigurationBase
from atlassian import Confluence
from typing import List


def replace_content(client: Confluence, document_id: str, replacements: List[str]) -> {}:
    # read content based on document_id
    current_content = client.get_page_by_id(
        document_id, expand="body.storage", status=None, version=None
    )
    current_content_body = current_content["body"]["storage"]["value"]
    for k, v in replacements.items():
        if v:
            current_content_body = current_content_body.replace(k, v)

    updated_content = client.update_page(
        page_id=document_id,
        title=current_content["title"],
        body=current_content_body,
        representation="storage",
        type="page",
        parent_id=None,
        minor_edit=False,
        full_width=False,
    )
    return updated_content


class ConfluencePageDocPlugin(DocumentPlugin):
    title = "Confluence pages plugin - Document Management"
    slug = "confluence-docs-document"
    description = "Use Confluence to update the contents."
    version = confluence_doc_plugin.__version__

    author = "Cino Jose"
    author_url = "https://github.com/Netflix/dispatch"

    def __init__(self):
        self.configuration_schema = ConfluenceConfigurationBase

    def update(self, document_id: str, **kwargs):
        """Replaces text in document."""
        kwargs = {"{{" + k + "}}": v for k, v in kwargs.items()}
        confluence_client = Confluence(
            url=self.configuration.api_url,
            username=self.configuration.username,
            password=self.configuration.password.get_secret_value(),
            cloud=self.configuration.hosting_type,
        )
        return replace_content(confluence_client, document_id, kwargs)
