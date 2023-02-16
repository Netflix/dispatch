from dispatch.plugins import dispatch_atlassian_confluence as confluence_plugin
from dispatch.plugins.bases import StoragePlugin
from dispatch.plugins.dispatch_atlassian_confluence.config import ConfluenceConfigurationBase

from pydantic import Field

from atlassian import Confluence
import requests
from requests.auth import HTTPBasicAuth
import logging
from typing import List

logger = logging.getLogger(__name__)


# TODO : Use the common config from the root directory.
class ConfluenceConfiguration(ConfluenceConfigurationBase):
    """Confluence configuration description."""

    template_id: str = Field(
        title="Incident template ID", description="This is the page id of the template."
    )
    root_id: str = Field(
        title="Default Space ID", description="Defines the default Confluence Space to use."
    )
    parent_id: str = Field(
        title="Parent ID for the pages",
        description="Define the page id of a parent page where all the incident documents can be kept.",
    )
    open_on_close: bool = Field(
        title="Open On Close",
        default=False,
        description="Controls the visibility of resources on incident close. If enabled Dispatch will make all resources visible to the entire workspace.",
    )
    read_only: bool = Field(
        title="Readonly",
        default=False,
        description="The incident document will be marked as readonly on incident close. Participants will still be able to interact with the document but any other viewers will not.",
    )


class ConfluencePagePlugin(StoragePlugin):
    title = "Confluence Plugin - Store your incident details"
    slug = "confluence"
    description = "Confluence plugin to create incident documents"
    version = confluence_plugin.__version__

    author = "Cino Jose"
    author_url = "https://github.com/Netflix/dispatch"

    def __init__(self):
        self.configuration_schema = ConfluenceConfiguration

    def create_file(
        self, drive_id: str, name: str, participants: List[str] = None, file_type: str = "folder"
    ):
        """Creates a new Home page for the incident documents.."""
        try:
            if file_type not in ["document", "folder"]:
                return None
            confluence_client = Confluence(
                url=self.configuration.api_url,
                username=self.configuration.username,
                password=self.configuration.password.get_secret_value(),
                cloud=self.configuration.hosting_type,
            )
            child_display_body = """<h3>Incident Documents:</h3><ac:structured-macro ac:name="children"
                                    ac:schema-version="2" data-layout="default" ac:local-id="ec0e8d6d-3215-4328-b1f8-e96b03ccefb9"
                                    ac:macro-id="10235d28b48543519d4e2b06ca230142"><ac:parameter ac:name="sort">modified</ac:parameter>
                                    <ac:parameter ac:name="reverse">true</ac:parameter></ac:structured-macro>"""
            page_details = confluence_client.create_page(
                drive_id,
                name,
                body=child_display_body,
                parent_id=self.configuration.parent_id,
                type="page",
                representation="storage",
                editor="v2",
                full_width=False,
            )
            return {
                "weblink": f"{self.configuration.api_url}wiki/spaces/{drive_id}/pages/{page_details['id']}/{name}",
                "id": page_details["id"],
                "name": name,
                "description": "",
            }
        except Exception as e:
            logger.error(f"Exception happened while creating page: {e}")

    def copy_file(self, folder_id: str, file_id: str, name: str):
        # TODO : This is the function that is responsible for making the incident documents.
        try:
            confluence_client = Confluence(
                url=self.configuration.api_url,
                username=self.configuration.username,
                password=self.configuration.password.get_secret_value(),
                cloud=self.configuration.hosting_type,
            )
            logger.info(f"Copy_file function with args {folder_id}, {file_id}, {name}")
            template_content = confluence_client.get_page_by_id(
                self.configuration.template_id, expand="body.storage", status=None, version=None
            )
            page_details = confluence_client.create_page(
                space=self.configuration.root_id,
                parent_id=folder_id,
                title=name,
                type="page",
                body=template_content["body"],
                representation="storage",
                editor="v2",
                full_width=False,
            )
            if self.configuration.parent_id:
                """TODO: Find and fix why the page is not created under the parent_id, folder_id"""
                self.move_file_confluence(page_id_to_move=page_details["id"], parent_id=folder_id)
            return {
                "weblink": f"{self.configuration.api_url}wiki/spaces/{folder_id}/pages/{page_details['id']}/{name}",
                "id": page_details["id"],
                "name": name,
            }
        except Exception as e:
            logger.error(f"Exception happened while creating page: {e}")

    def move_file(self, new_folder_id: str, file_id: str, **kwargs):
        """Moves a file from one place to another. Not used in the plugin,
        keeping the body as the interface is needed to avoid exceptions."""
        return {}

    def move_file_confluence(self, page_id_to_move: str, parent_id: str):
        try:
            url = f"{self.configuration.api_url}wiki/rest/api/content/{page_id_to_move}/move/append/{parent_id}"
            auth = HTTPBasicAuth(
                self.configuration.username, self.configuration.password.get_secret_value()
            )
            headers = {"Accept": "application/json"}
            response = requests.request("PUT", url, headers=headers, auth=auth)
            return response
        except Exception as e:
            logger.error(f"Exception happened while moving page: {e}")
