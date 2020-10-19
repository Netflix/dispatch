"""
.. module: dispatch.plugins.dispatch_slack.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from joblib import Memory
from typing import List, Optional
import logging
import os
import re
import slack

from dispatch.conversation.enums import ConversationCommands
from dispatch.decorators import apply, counter, timer
from dispatch.exceptions import DispatchPluginException
from dispatch.plugins import dispatch_slack as slack_plugin
from dispatch.plugins.bases import ConversationPlugin, DocumentPlugin, ContactPlugin

from .config import (
    SLACK_API_BOT_TOKEN,
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_REPORT_EXECUTIVE_SLUG,
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    SLACK_COMMAND_LIST_RESOURCES_SLUG,
    SLACK_COMMAND_LIST_TASKS_SLUG,
    SLACK_COMMAND_REPORT_TACTICAL_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    SLACK_PROFILE_DEPARTMENT_FIELD_ID,
    SLACK_PROFILE_TEAM_FIELD_ID,
    SLACK_PROFILE_WEBLINK_FIELD_ID,
)
from .views import router as slack_event_router
from .messaging import create_message_blocks
from .service import (
    add_users_to_conversation,
    archive_conversation,
    unarchive_conversation,
    create_conversation,
    get_conversation_by_name,
    get_user_avatar_url,
    get_user_email,
    get_user_info_by_id,
    get_user_profile_by_email,
    get_user_username,
    list_conversation_messages,
    list_conversations,
    message_filter,
    open_dialog_with_user,
    open_modal_with_user,
    resolve_user,
    send_ephemeral_message,
    send_message,
    set_conversation_topic,
)


logger = logging.getLogger(__name__)

command_mappings = {
    ConversationCommands.assign_role: SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    ConversationCommands.update_incident: SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    ConversationCommands.engage_oncall: SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    ConversationCommands.executive_report: SLACK_COMMAND_REPORT_EXECUTIVE_SLUG,
    ConversationCommands.list_participants: SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    ConversationCommands.list_resources: SLACK_COMMAND_LIST_RESOURCES_SLUG,
    ConversationCommands.list_tasks: SLACK_COMMAND_LIST_TASKS_SLUG,
    ConversationCommands.tactical_report: SLACK_COMMAND_REPORT_TACTICAL_SLUG,
}


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class SlackConversationPlugin(ConversationPlugin):
    title = "Slack Plugin - Conversation Management"
    slug = "slack-conversation"
    description = "Uses Slack to facilitate conversations."
    version = slack_plugin.__version__
    events = slack_event_router

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.client = slack.WebClient(token=str(SLACK_API_BOT_TOKEN))

    def create(self, name: str, participants: List[dict], is_private: bool = True):
        """Creates a new slack conversation."""
        participants = [resolve_user(self.client, p)["id"] for p in participants]
        return create_conversation(self.client, name, participants, is_private)

    def send(
        self,
        conversation_id: str,
        text: str,
        message_template: List[dict],
        notification_type: str,
        items: Optional[List] = None,
        blocks: Optional[List] = None,
        persist: bool = False,
        **kwargs,
    ):
        """Sends a new message based on data and type."""
        if not blocks:
            blocks = create_message_blocks(message_template, notification_type, items, **kwargs)

        return send_message(self.client, conversation_id, text, blocks, persist)

    def send_direct(
        self,
        user: str,
        text: str,
        message_template: dict,
        notification_type: str,
        items: Optional[List] = None,
        blocks: Optional[List] = None,
        **kwargs,
    ):
        """Sends a message directly to a user."""
        user_id = resolve_user(self.client, user)["id"]

        if not blocks:
            blocks = create_message_blocks(message_template, notification_type, items, **kwargs)

        return send_message(self.client, user_id, text, blocks)

    def send_ephemeral(
        self,
        conversation_id: str,
        user: str,
        text: str,
        message_template: dict = None,
        notification_type: str = None,
        items: Optional[List] = None,
        blocks: Optional[List] = None,
        **kwargs,
    ):
        """Sends an ephemeral message to a user in a channel."""
        user_id = resolve_user(self.client, user)["id"]

        if not blocks:
            blocks = create_message_blocks(message_template, notification_type, items, **kwargs)

        return send_ephemeral_message(self.client, conversation_id, user_id, text, blocks)

    def add(self, conversation_id: str, participants: List[str]):
        """Adds users to conversation."""
        participants = [resolve_user(self.client, p)["id"] for p in participants]
        return add_users_to_conversation(self.client, conversation_id, participants)

    def open_dialog(self, trigger_id: str, dialog: dict):
        """Opens a dialog with a user."""
        return open_dialog_with_user(self.client, trigger_id, dialog)

    def archive(self, conversation_id: str):
        """Archives conversation."""
        return archive_conversation(self.client, conversation_id)

    def unarchive(self, conversation_id: str):
        """Unarchives conversation."""
        return unarchive_conversation(self.client, conversation_id)

    def get_participant_username(self, participant_id: str):
        """Gets the participant's username."""
        return get_user_username(self.client, participant_id)

    def get_participant_email(self, participant_id: str):
        """Gets the participant's email."""
        return get_user_email(self.client, participant_id)

    def get_participant_avatar_url(self, participant_id: str):
        """Gets the participant's avatar url."""
        return get_user_avatar_url(self.client, participant_id)

    def set_topic(self, conversation_id: str, topic: str):
        """Sets the conversation topic."""
        return set_conversation_topic(self.client, conversation_id, topic)

    def get_command_name(self, command: str):
        """Gets the command name."""
        return command_mappings.get(command, [])

    def open_modal(self, trigger_id: str, modal: dict):
        """Opens a modal with a user."""
        return open_modal_with_user(client=self.client, trigger_id=trigger_id, modal=modal)


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class SlackContactPlugin(ContactPlugin):
    title = "Slack Plugin - Contact Information Resolver"
    slug = "slack-contact"
    description = "Uses Slack to resolve contact information details."
    version = slack_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.client = slack.WebClient(token=str(SLACK_API_BOT_TOKEN))

    def get(self, email: str, **kwargs):
        """Fetch user info by email."""
        team = department = weblink = "Unknown"

        profile = get_user_profile_by_email(self.client, email)
        profile_fields = profile.get("fields")
        if profile_fields:
            team = profile_fields.get(SLACK_PROFILE_TEAM_FIELD_ID, {}).get("value", "Unknown")
            department = profile_fields.get(SLACK_PROFILE_DEPARTMENT_FIELD_ID, {}).get(
                "value", "Unknown"
            )
            weblink = profile_fields.get(SLACK_PROFILE_WEBLINK_FIELD_ID, {}).get("value", "Unknown")

        return {
            "fullname": profile["real_name"],
            "email": profile["email"],
            "title": profile["title"],
            "team": team,
            "department": department,
            "location": profile["tz"],
            "weblink": weblink,
            "thumbnail": profile["image_512"],
        }


class SlackDocumentPlugin(DocumentPlugin):
    title = "Slack Plugin - Document Interrogator"
    slug = "slack-document"
    description = "Uses Slack as a document source."
    version = slack_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.cachedir = os.path.dirname(os.path.realpath(__file__))
        self.memory = Memory(cachedir=self.cachedir, verbose=0)
        self.client = slack.WebClient(token=str(SLACK_API_BOT_TOKEN))

    def get(self, **kwargs) -> dict:
        """Queries slack for documents."""
        conversations = []

        if kwargs["channels"]:
            logger.debug(f"Querying slack for documents. Channels: {kwargs['channels']}")

            channels = kwargs["channels"].split(",")
            for c in channels:
                conversations.append(get_conversation_by_name(self.client, c))

        if kwargs["channel_match_pattern"]:
            try:
                regex = kwargs["channel_match_pattern"]
                pattern = re.compile(regex)
            except re.error as e:
                raise DispatchPluginException(
                    message=f"Invalid regex. Is everything escaped properly? Regex: '{regex}' Message: {e}"
                )

            logger.debug(
                f"Querying slack for documents. ChannelsPattern: {kwargs['channel_match_pattern']}"
            )
            for c in list_conversations(self.client):
                if pattern.match(c["name"]):
                    conversations.append(c)

        for c in conversations:
            logger.info(f'Fetching channel messages. Channel Name: {c["name"]}')

            messages = list_conversation_messages(self.client, c["id"], lookback=kwargs["lookback"])

            logger.info(f'Found {len(messages)} messages in slack. Channel Name: {c["name"]}')

            for m in messages:
                if not message_filter(m):
                    continue

                user_email = get_user_info_by_id(self.client, m["user"])["user"]["profile"]["email"]

                yield {
                    "person": {"email": user_email},
                    "doc": {
                        "text": m["text"],
                        "is_private": c["is_private"],
                        "subject": c["name"],
                        "source": "slack",
                    },
                    "ref": {"timestamp": m["ts"]},
                }
