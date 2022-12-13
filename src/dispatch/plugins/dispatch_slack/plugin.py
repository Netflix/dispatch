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

from dispatch.conversation.enums import ConversationCommands
from dispatch.decorators import apply, counter, timer
from dispatch.exceptions import DispatchPluginException
from dispatch.plugins import dispatch_slack as slack_plugin
from dispatch.plugins.bases import ConversationPlugin, DocumentPlugin, ContactPlugin
from dispatch.plugins.dispatch_slack.config import (
    SlackConfiguration,
    SlackContactConfiguration,
    SlackConversationConfiguration,
)

from .bolt import router as slack_event_router
from .messaging import create_message_blocks
from .service import (
    add_users_to_conversation,
    archive_conversation,
    chunks,
    conversation_archived,
    create_conversation,
    create_slack_client,
    get_conversation_by_name,
    get_user_avatar_url,
    get_user_info_by_id,
    get_user_profile_by_email,
    list_conversation_messages,
    list_conversations,
    message_filter,
    resolve_user,
    send_ephemeral_message,
    send_message,
    set_conversation_topic,
    unarchive_conversation,
)


logger = logging.getLogger(__name__)


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
        self.configuration_schema = SlackConversationConfiguration

    def create(self, name: str):
        """Creates a new Slack conversation."""
        client = create_slack_client(self.configuration)
        return create_conversation(client, name, self.configuration.private_channels)

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
        client = create_slack_client(self.configuration)
        if not blocks:
            blocks = create_message_blocks(message_template, notification_type, items, **kwargs)

        messages = []
        for c in chunks(blocks, 50):
            messages.append(send_message(client, conversation_id, text, c, persist))
        return messages

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
        client = create_slack_client(self.configuration)
        user_id = resolve_user(client, user)["id"]

        if not blocks:
            blocks = create_message_blocks(message_template, notification_type, items, **kwargs)

        return send_message(client, user_id, text, blocks)

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
        client = create_slack_client(self.configuration)
        user_id = resolve_user(client, user)["id"]

        if not blocks:
            blocks = create_message_blocks(message_template, notification_type, items, **kwargs)

        archived = conversation_archived(client, conversation_id)
        if not archived:
            send_ephemeral_message(client, conversation_id, user_id, text, blocks)

    def add(self, conversation_id: str, participants: List[str]):
        """Adds users to conversation."""
        client = create_slack_client(self.configuration)
        participants = [resolve_user(client, p)["id"] for p in participants]

        archived = conversation_archived(client, conversation_id)
        if not archived:
            add_users_to_conversation(client, conversation_id, participants)

    def archive(self, conversation_id: str):
        """Archives conversation."""
        client = create_slack_client(self.configuration)
        return archive_conversation(client, conversation_id)

    def unarchive(self, conversation_id: str):
        """Unarchives conversation."""
        client = create_slack_client(self.configuration)
        return unarchive_conversation(client, conversation_id)

    def get_participant_avatar_url(self, participant_id: str):
        """Gets the participant's avatar url."""
        client = create_slack_client(self.configuration)
        return get_user_avatar_url(client, participant_id)

    def set_topic(self, conversation_id: str, topic: str):
        """Sets the conversation topic."""
        client = create_slack_client(self.configuration)
        return set_conversation_topic(client, conversation_id, topic)

    def get_command_name(self, command: str):
        """Gets the command name."""
        command_mappings = {
            ConversationCommands.assign_role: self.configuration.slack_command_assign_role,
            ConversationCommands.update_incident: self.configuration.slack_command_update_incident,
            ConversationCommands.engage_oncall: self.configuration.slack_command_engage_oncall,
            ConversationCommands.executive_report: self.configuration.slack_command_report_executive,
            ConversationCommands.list_participants: self.configuration.slack_command_list_participants,
            ConversationCommands.list_resources: self.configuration.slack_command_list_resources,
            ConversationCommands.list_tasks: self.configuration.slack_command_list_tasks,
            ConversationCommands.tactical_report: self.configuration.slack_command_report_tactical,
        }
        return command_mappings.get(command, [])


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
        self.configuration_schema = SlackContactConfiguration

    def get(self, email: str, **kwargs):
        """Fetch user info by email."""
        client = create_slack_client(self.configuration)
        team = department = "Unknown"
        weblink = ""

        profile = get_user_profile_by_email(client, email)
        profile_fields = profile.get("fields")
        if profile_fields:
            team = profile_fields.get(self.configuration.profile_team_field_id, {}).get(
                "value", "Unknown"
            )
            department = profile_fields.get(self.configuration.profile_department_field_id, {}).get(
                "value", "Unknown"
            )
            weblink = profile_fields.get(self.configuration.profile_weblink_field_id, {}).get(
                "value", ""
            )

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
        self.configuration_schema = SlackConfiguration
        self.cachedir = os.path.dirname(os.path.realpath(__file__))
        self.memory = Memory(cachedir=self.cachedir, verbose=0)

    def get(self, **kwargs) -> dict:
        """Queries slack for documents."""
        client = create_slack_client(self.configuration)
        conversations = []

        if kwargs["channels"]:
            logger.debug(f"Querying slack for documents. Channels: {kwargs['channels']}")

            channels = kwargs["channels"].split(",")
            for c in channels:
                conversations.append(get_conversation_by_name(client, c))

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
            for c in list_conversations(client):
                if pattern.match(c["name"]):
                    conversations.append(c)

        for c in conversations:
            logger.info(f'Fetching channel messages. Channel Name: {c["name"]}')

            messages = list_conversation_messages(client, c["id"], lookback=kwargs["lookback"])

            logger.info(f'Found {len(messages)} messages in slack. Channel Name: {c["name"]}')

            for m in messages:
                if not message_filter(m):
                    continue

                user_email = get_user_info_by_id(client, m["user"])["user"]["profile"]["email"]

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
