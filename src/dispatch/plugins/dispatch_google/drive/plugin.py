from typing import List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import StoragePlugin, TaskPlugin
from dispatch.plugins.dispatch_google import drive as google_drive_plugin
from dispatch.plugins.dispatch_google.common import get_service

from dispatch.plugins.dispatch_google.config import GOOGLE_DOMAIN
from .drive import (
    Roles,
    add_permission,
    copy_file,
    create_file,
    delete_file,
    download_google_document,
    list_files,
    move_file,
    remove_permission,
    add_domain_permission,
    add_reply,
)
from .task import list_tasks


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleDriveStoragePlugin(StoragePlugin):
    title = "Google Drive Plugin - Storage Management"
    slug = "google-drive-storage"
    description = "Uses Google Drive to help manage incident storage."
    version = google_drive_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    _schema = None

    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/drive"]

    def get(self, file_id: str, mime_type=None):
        """Fetches document text."""
        client = get_service("drive", "v3", self.scopes)
        return download_google_document(client, file_id, mime_type=mime_type)

    def add_participant(
        self,
        team_drive_or_file_id: str,
        participants: List[str],
        role: str = "owner",
        user_type: str = "user",
    ):
        """Adds participants to existing Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        for p in participants:
            add_permission(client, p, team_drive_or_file_id, role, user_type)

    def remove_participant(self, folder_id: str, participants: List[str]):
        """Removes participants from existing Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        for p in participants:
            remove_permission(client, p, folder_id)

    def open(self, folder_id: str):
        """Adds the domain permission to the folder."""
        client = get_service("drive", "v3", self.scopes)
        add_domain_permission(client, folder_id, GOOGLE_DOMAIN)

    def create_file(
        self,
        parent_id: str,
        name: str,
        participants: List[str] = [],
        role: str = Roles.writer.value,
        file_type: str = "folder",
    ):
        """Creates a new file in existing Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        response = create_file(client, parent_id, name, participants, role, file_type)
        response["weblink"] = response["webViewLink"]
        return response

    def delete_file(self, folder_id: str, file_id: str):
        """Removes a file from existing Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        response = delete_file(client, folder_id, file_id)
        response["weblink"] = response["webViewLink"]
        return response

    def copy_file(self, folder_id: str, file_id: str, name: str):
        """Creates a copy of the given file and places it in the specified team drive."""
        client = get_service("drive", "v3", self.scopes)
        response = copy_file(client, folder_id, file_id, name)
        response["weblink"] = response["webViewLink"]
        return response

    def move_file(self, new_folder_id: str, file_id: str):
        """Moves a file from one team drive to another."""
        client = get_service("drive", "v3", self.scopes)
        response = move_file(client, new_folder_id, file_id)
        response["weblink"] = response["webViewLink"]
        return response

    def list_files(self, folder_id: str, q: str = None):
        """Lists all files in team drive."""
        client = get_service("drive", "v3", self.scopes)
        return list_files(client, folder_id, q)


class GoogleDriveTaskPlugin(TaskPlugin):
    title = "Google Drive Plugin - Task Management"
    slug = "google-drive-task"
    description = "Uses Google Drive to help manage incident tasks."
    version = google_drive_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    _schema = None

    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/drive"]

    def create(self, file_id: str, text: str):
        """Creates a new task."""
        pass

    def update(self, file_id: str, task_id: str, content: str = None, resolved: bool = False):
        """Updates an existing task."""
        client = get_service("drive", "v3", self.scopes)
        return add_reply(client, file_id, task_id, content, resolved)

    def list(self, file_id: str, **kwargs):
        """Lists all available tasks."""
        client = get_service("drive", "v3", self.scopes)
        return list_tasks(client, file_id)
