from typing import List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import StoragePlugin, TaskPlugin
from dispatch.plugins.dispatch_google import drive as google_drive_plugin
from dispatch.plugins.dispatch_google.common import get_service

from .drive import (
    Roles,
    add_permission,
    archive_team_drive,
    copy_file,
    create_file,
    create_team_drive,
    delete_file,
    delete_team_drive,
    download_google_document,
    list_files,
    list_team_drives,
    move_file,
    remove_permission,
    restrict_team_drive,
    unrestrict_team_drive,
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

    def create(self, name: str, participants: List[str], role: str = Roles.file_organizer.value):
        """Creates a new Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        response = create_team_drive(client, name, participants, role)
        response["weblink"] = f"https://drive.google.com/drive/folders/{response['id']}"
        return response

    def delete(self, team_drive_id: str, empty: bool = True):
        """Deletes a Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        return delete_team_drive(client, team_drive_id, empty)

    def list(self, **kwargs):
        """Lists all available team drives."""
        client = get_service("drive", "v3", self.scopes)
        return list_team_drives(client, **kwargs)

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

    def remove_participant(self, team_drive_id: str, participants: List[str]):
        """Removes participants from existing Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        for p in participants:
            remove_permission(client, p, team_drive_id)

    def create_file(self, team_drive_id: str, name: str, file_type: str = "folder"):
        """Creates a new file in existing Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        response = create_file(client, team_drive_id, name, file_type)
        response["weblink"] = response["webViewLink"]
        return response

    def delete_file(self, team_drive_id: str, file_id: str):
        """Removes a file from existing Google Drive."""
        client = get_service("drive", "v3", self.scopes)
        response = delete_file(client, team_drive_id, file_id)
        response["weblink"] = response["webViewLink"]
        return response

    def copy_file(self, team_drive_id: str, file_id: str, name: str):
        """Creates a copy of the given file and places it in the specified team drive."""
        client = get_service("drive", "v3", self.scopes)
        response = copy_file(client, team_drive_id, file_id, name)
        response["weblink"] = response["webViewLink"]
        return response

    def move_file(self, new_team_drive_id: str, file_id: str):
        """Moves a file from one team drive to another."""
        client = get_service("drive", "v3", self.scopes)
        response = move_file(client, new_team_drive_id, file_id)
        response["weblink"] = response["webViewLink"]
        return response

    def archive(self, source_team_drive_id: str, dest_team_drive_id: str, folder_name: str):
        """Archives a shared team drive to a specific folder."""
        client = get_service("drive", "v3", self.scopes)
        response = archive_team_drive(client, source_team_drive_id, dest_team_drive_id, folder_name)
        return response

    def list_files(self, team_drive_id: str, q: str = None):
        """Lists all files in team drive."""
        client = get_service("drive", "v3", self.scopes)
        return list_files(client, team_drive_id, q)

    def restrict(self, team_drive_id: str):
        """Applies a set of restrictions and capabilities to the team drive."""
        client = get_service("drive", "v3", self.scopes)
        response = restrict_team_drive(client, team_drive_id)
        return response

    def unrestrict(self, team_drive_id: str):
        """Removes a set of restrictions and capabilities from the team drive."""
        client = get_service("drive", "v3", self.scopes)
        response = unrestrict_team_drive(client, team_drive_id)
        return response


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

    def update(self, file_id: str, task_id):
        """Updates an existing task."""
        pass

    def list(self, file_id: str, **kwargs):
        """Lists all available tasks."""
        client = get_service("drive", "v3", self.scopes)
        return list_tasks(client, file_id)
