import json
import logging

from starlette.requests import Request
from slack_sdk.web.client import WebClient

from dispatch.database.core import SessionLocal
from dispatch.database.service import search_filter_sort_paginate
from dispatch.incident import service as incident_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.modals.common import parse_submitted_form
from dispatch.plugins.dispatch_slack.modals.incident.enums import IncidentBlockId

log = logging.getLogger(__name__)


async def handle_slack_menu(*, db_session: SessionLocal, client: WebClient, request: Request):
    """Handles slack menu message."""
    # We resolve the user's email
    user_id = request["user"]["id"]
    user_email = await dispatch_slack_service.get_user_email_async(client, user_id)

    request["user"]["email"] = user_email

    # When there are no exceptions within the dialog submission, your app must respond with 200 OK with an empty body.
    view_data = request["view"]
    view_data["private_metadata"] = json.loads(view_data["private_metadata"])
    query_str = request.get("value")

    incident_id = view_data["private_metadata"].get("incident_id")
    channel_id = view_data["private_metadata"].get("channel_id")
    action_id = request["action_id"]

    f = menu_functions(action_id)
    return f(db_session, user_id, user_email, channel_id, incident_id, query_str, request)


def menu_functions(action_id: str):
    """Handles all menu requests."""
    menu_mappings = {IncidentBlockId.tags: get_tags}

    for key in menu_mappings.keys():
        if key in action_id:
            return menu_mappings[key]

    raise Exception(f"No menu function found. actionId: {action_id}")


def get_tags(
    db_session: SessionLocal,
    user_id: int,
    user_email: str,
    channel_id: str,
    incident_id: str,
    query_str: str,
    request: Request,
):
    """Fetches tags based on the current query."""
    # use the project from the incident if available
    filter_spec = {}
    if incident_id:
        incident = incident_service.get(db_session=db_session, incident_id=incident_id)
        # scope to current incident project
        filter_spec = {
            "and": [{"model": "Project", "op": "==", "field": "id", "value": incident.project.id}]
        }

    submitted_form = request.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)
    project = parsed_form_data.get(IncidentBlockId.project)

    if project:
        filter_spec = {
            "and": [{"model": "Project", "op": "==", "field": "name", "value": project["value"]}]
        }

    # attempt to filter by tag type
    if "/" in query_str:
        tag_type, tag_name = query_str.split("/")
        type_filter = {"model": "TagType", "op": "==", "field": "name", "value": tag_type}

        if filter_spec.get("and"):
            filter_spec["and"].append(type_filter)
        else:
            filter_spec = {"and": [type_filter]}

        if not len(tag_name):
            query_str = None

        tags = search_filter_sort_paginate(
            db_session=db_session, model="Tag", query_str=query_str, filter_spec=filter_spec
        )
    else:
        tags = search_filter_sort_paginate(
            db_session=db_session, model="Tag", query_str=query_str, filter_spec=filter_spec
        )

    options = []
    for t in tags["items"]:
        options.append(
            {
                "text": {"type": "plain_text", "text": f"{t.tag_type.name}/{t.name}"},
                "value": str(
                    t.id
                ),  # NOTE slack doesn't not accept int's as values (fails silently)
            }
        )

    return {"options": options}
