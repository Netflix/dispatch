from typing import List
from pydantic import Field

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import StoragePlugin, TaskPlugin
from dispatch.plugins.dispatch_google import drive as google_drive_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import GoogleConfiguration

from .drive import (
    Roles,
    UserTypes,
    add_domain_permission,
    add_permission,
    add_reply,
    copy_file,
    create_file,
    delete_file,
    download_google_document,
    list_files,
    mark_as_readonly,
    move_file,
    remove_permission,
)
from .task import get_task_activity


class GoogleDriveConfiguration(GoogleConfiguration):
    """Google drive configuration."""

    root_id: str = Field(
        title="Root Incident Storage FolderId",
        description="This is the default folder for all incident data. Dispatch will create subfolders for each incident in this folder.",
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


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleDriveStoragePlugin(StoragePlugin):
    title = "Google Drive Plugin - Storage Management"
    slug = "google-drive-storage"
    description = "Uses Google Drive to help manage incident storage."
    version = google_drive_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = GoogleDriveConfiguration
        self.scopes = ["https://www.googleapis.com/auth/drive"]

    def get(self, file_id: str, mime_type=None):
        """Fetches document text."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        return download_google_document(client, file_id, mime_type=mime_type)

    def add_participant(
        self,
        team_drive_or_file_id: str,
        participants: List[str],
        role: str = Roles.writer,
        user_type: str = UserTypes.user,
    ):
        """Adds participants to an existing Google Drive."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        for p in participants:
            add_permission(client, p, team_drive_or_file_id, role, user_type)

    def remove_participant(self, team_drive_or_file_id: str, participants: List[str]):
        """Removes participants from an existing Google Drive."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        for p in participants:
            remove_permission(client, p, team_drive_or_file_id)

    def open(self, folder_id: str):
        """Adds the domain permission to the folder."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        add_domain_permission(client, folder_id, self.configuration.google_domain)

    def mark_readonly(self, file_id: str):
        """Adds the read only permission to the folder."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        mark_as_readonly(client, file_id)

    def create_file(
        self,
        parent_id: str,
        name: str,
        participants: List[str] = None,
        role: str = Roles.writer,
        file_type: str = "folder",
    ):
        """Creates a new file in an existing Google Drive."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        response = create_file(client, parent_id, name, participants, role, file_type)
        response["weblink"] = response["webViewLink"]
        return response

    def delete_file(self, file_id: str):
        """Deletes a file or folder from an existing Google Drive."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        response = delete_file(client, file_id)
        return response

    def copy_file(self, folder_id: str, file_id: str, name: str):
        """Creates a copy of the given file and places it in the specified Google Drive."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        response = copy_file(client, folder_id, file_id, name)
        response["weblink"] = response["webViewLink"]
        return response

    def move_file(self, new_folder_id: str, file_id: str):
        """Moves a file from one Google drive to another."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        response = move_file(client, new_folder_id, file_id)
        response["weblink"] = response["webViewLink"]
        return response

    def list_files(self, folder_id: str, q: str = None):
        """Lists all files in a Google drive."""
        client = get_service(self.configuration, "drive", "v3", self.scopes)
        return list_files(client, folder_id, q)


class GoogleDriveTaskPlugin(TaskPlugin):
    title = "Google Drive Plugin - Task Management"
    slug = "google-drive-task"
    description = "Uses Google Drive to help manage incident tasks."
    version = google_drive_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = GoogleConfiguration
        self.scopes = ["https://www.googleapis.com/auth/drive"]

    def create(self, file_id: str, text: str):
        """Creates a new task."""
        pass

    def update(self, file_id: str, task_id: str, content: str = None, resolved: bool = False):
        """Updates an existing task."""
        client = get_service(
            self.configuration, "drive", "v3", ["https://www.googleapis.com/auth/drive"]
        )
        return add_reply(client, file_id, task_id, content, resolved)

    def list(self, file_id: str, lookback: int = 60, **kwargs):
        """Lists all available tasks."""
        activity_client = get_service(
            self.configuration,
            "driveactivity",
            "v2",
            ["https://www.googleapis.com/auth/drive.activity.readonly"],
        )
        comment_client = get_service(
            self.configuration, "drive", "v3", ["https://www.googleapis.com/auth/drive"]
        )
        people_client = get_service(
            self.configuration,
            "people",
            "v1",
            ["https://www.googleapis.com/auth/contacts.readonly"],
        )
        return get_task_activity(activity_client, comment_client, people_client, file_id, lookback)
