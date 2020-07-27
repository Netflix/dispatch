"""
.. module: dispatch.plugins.google_drive.drive
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import functools
import io
import json
import logging
import tempfile
from enum import Enum
from typing import Any, List

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt, wait_exponential


log = logging.getLogger(__name__)


class UserTypes(str, Enum):
    user = "user"
    group = "group"
    domain = "domain"
    anyone = "anyone"


class Roles(str, Enum):
    owner = "owner"
    organizer = "organizer"
    file_organizer = "fileOrganizer"
    writer = "writer"
    commenter = "commenter"
    reader = "reader"


def paginated(data_key):
    def decorator(func):
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            results = []
            limit = int(kwargs.pop("limit", 250))
            while True:
                # auto add next page token for pagination
                if kwargs.get("fields"):
                    fields = kwargs["fields"].split(",")
                    if "nextPageToken" not in fields:
                        fields.append("nextPageToken")

                    kwargs["fields"] = ",".join(fields)

                response = func(*args, **kwargs)
                results += response.get(data_key)

                # stop if we hit an empty string
                next_token = response.get("nextPageToken")
                if not next_token:
                    break

                kwargs.update({"pageToken": next_token})

                if len(results) > limit:
                    break

            return results

        return decorated_function

    return decorator


# google sometimes has transient errors
@retry(
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(TryAgain),
    wait=wait_exponential(multiplier=1, min=2, max=5),
)
def make_call(client: Any, func: Any, propagate_errors: bool = False, **kwargs):
    """Make an Google client api call."""
    try:
        return getattr(client, func)(**kwargs).execute()
    except HttpError as e:
        if e.resp.status in [300, 429, 500, 502, 503, 504]:
            log.debug("Google encountered an error retrying...")
            raise TryAgain

        if propagate_errors:
            raise HttpError

        errors = json.loads(e.content.decode())
        raise Exception(f"Request failed. Errors: {errors}")


@retry(wait=wait_exponential(multiplier=1, max=10))
def upload_chunk(request: Any):
    """Uploads a check of data."""
    try:
        return request.next_chunk()
    except HttpError as e:
        if e.resp.status in [500, 502, 503, 504]:
            # Call next_chunk() agai, but use an exponential backoff for repeated errors.
            raise e


#  TODO add retry
def upload_file(client: Any, path: str, name: str, mimetype: str):
    """Uploads a file."""
    media = MediaFileUpload(path, mimetype=mimetype, resumable=True)

    try:
        request = client.files().create(media_body=media, body={"name": name})
        response = None

        while not response:
            _, response = upload_chunk(request)
        return response
    except HttpError as e:
        if e.resp.status in [404]:
            # Start the upload all over again.
            raise TryAgain
        else:
            raise Exception(
                f"Failed to upload file. Name: {name} Path: {path} MIMEType: {mimetype}"
            )


def get_file(client: Any, file_id: str):
    """Gets a file's metadata."""
    return make_call(
        client.files(),
        "get",
        fileId=file_id,
        fields="id, name, parents, webViewLink",
        supportsAllDrives=True,
    )


#  TODO add retry
def download_file(client: Any, file_id: str):
    """Downloads a file."""
    request = client.files().get_media(fileId=file_id)
    fp = tempfile.NamedTemporaryFile()
    downloader = MediaIoBaseDownload(fp, request)

    response = False
    try:
        while not response:
            _, response = downloader.next_chunk()
        return fp
    except HttpError:
        # Do not retry. Log the error and fail.
        raise Exception(f"Failed to download file. Id: {file_id}")


def download_google_document(client: Any, file_id: str, mime_type: str = "text/plain"):
    """Downloads a Google document."""
    request = client.files().export_media(fileId=file_id, mimeType=mime_type)

    fp = io.BytesIO()
    downloader = MediaIoBaseDownload(fp, request)

    response = False

    try:
        while not response:
            _, response = downloader.next_chunk()
        return fp.getvalue().decode("utf-8")
    except (HttpError, OSError):
        # Do no retry. Log the error fail.
        raise Exception(f"Failed to export the file. Id: {file_id} MimeType: {mime_type}")


def create_file(
    client: Any,
    parent_id: str,
    name: str,
    members: List[str],
    role: Roles = Roles.writer.value,
    file_type: str = "folder",
):
    """Creates a new folder with the specified parents."""
    mimetype = "application/vnd.google-apps.document"
    if file_type == "folder":
        mimetype = "application/vnd.google-apps.folder"

    file_metadata = {"name": name, "mimeType": mimetype, "parents": [parent_id]}

    file_data = make_call(
        client.files(),
        "create",
        body=file_metadata,
        fields="id, name, parents, webViewLink",
        supportsAllDrives=True,
    )

    for member in members:
        add_permission(client, member, file_data["id"], role, "user")

    return file_data


@paginated("files")
def list_files(client: any, team_drive_id: str, q: str = None, **kwargs):
    """Lists all files for a given query."""
    return make_call(
        client.files(),
        "list",
        corpora="drive",
        driveId=team_drive_id,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        q=q,
        **kwargs,
    )


@paginated("teamDrives")
def list_team_drives(client, **kwargs):
    """Lists all available team drives."""
    return make_call(client.teamdrives(), "list", **kwargs)


@paginated("comments")
def list_comments(client: Any, file_id: str, **kwargs):
    """Lists all available comments on file."""
    return make_call(client.comments(), "list", fileId=file_id, fields="*", **kwargs)


def add_reply(
    client: Any, file_id: str, comment_id: str, content: str, resolved: bool = False, **kwargs
):
    """Adds a reply to a comment."""
    if resolved:
        action = "resolve"
        content = content if content else "Resolved by Dispatch"
    else:
        action = "reopen"
        content = content if content else "Reopened by Dispatch"

    body = {"content": content, "action": action}
    return make_call(
        client.replies(), "create", fileId=file_id, commentId=comment_id, fields="id", body=body
    )


def copy_file(client: Any, folder_id: str, file_id: str, new_file_name: str):
    """Copies a given file."""
    return make_call(
        client.files(),
        "copy",
        body={"name": new_file_name, "driveId": folder_id},
        fileId=file_id,
        fields="id, name, parents, webViewLink",
        supportsAllDrives=True,
    )


def delete_file(client: Any, folder_id: str, file_id: str):
    """Deletes a file from a teamdrive."""
    return make_call(client.files(), "delete", fileId=file_id, supportsAllDrives=True)


def add_domain_permission(
    client: Any,
    team_drive_or_file_id: str,
    domain: str,
    role: Roles = Roles.commenter,
    user_type: UserTypes = UserTypes.domain,
):
    """Adds a domain permission to team drive or file."""
    permission = {"type": user_type, "role": role, "domain": domain}
    return make_call(
        client.permissions(),
        "create",
        fileId=team_drive_or_file_id,
        body=permission,
        sendNotificationEmail=False,
        fields="id",
        supportsAllDrives=True,
    )


def add_permission(
    client: Any,
    email: str,
    team_drive_or_file_id: str,
    role: Roles = Roles.owner,
    user_type: UserTypes = UserTypes.user,
):
    """Adds a permission to team drive"""
    permission = {"type": user_type, "role": role, "emailAddress": email}
    return make_call(
        client.permissions(),
        "create",
        fileId=team_drive_or_file_id,
        body=permission,
        sendNotificationEmail=False,
        fields="id",
        supportsAllDrives=True,
    )


def remove_permission(client: Any, email: str, folder_id: str):
    """Removes permission from team drive or file."""
    permissions = make_call(
        client.permissions(),
        "list",
        fileId=folder_id,
        fields="permissions(id, emailAddress)",
        supportsAllDrives=True,
    )

    for p in permissions["permissions"]:
        if p["emailAddress"] == email:
            make_call(
                client.permissions(),
                "delete",
                fileId=folder_id,
                permissionId=p["id"],
                supportsAllDrives=True,
            )


def move_file(client: Any, folder_id: str, file_id: str):
    """Moves a file from one team drive to another"""
    f = make_call(client.files(), "get", fileId=file_id, fields="parents", supportsAllDrives=True)

    previous_parents = ",".join(f.get("parents"))

    return make_call(
        client.files(),
        "update",
        fileId=file_id,
        addParents=folder_id,
        removeParents=previous_parents,
        fields="id, name, parents, webViewLink",
        supportsAllDrives=True,
    )


def list_permissions(client: Any, **kwargs):
    """List all permissions for file."""
    return make_call(client.files(), "list", **kwargs)
