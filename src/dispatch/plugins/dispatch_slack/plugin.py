"""
.. module: dispatch.plugins.dispatch_slack.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""

import io
import json
import logging
from typing import Any
from blockkit import Message
from blockkit.surfaces import Block
from slack_sdk.errors import SlackApiError
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.case.models import Case
from dispatch.conversation.enums import ConversationCommands
from dispatch.decorators import apply, counter, timer
from dispatch.plugin import service as plugin_service
from dispatch.plugins import dispatch_slack as slack_plugin
from dispatch.plugins.bases import ContactPlugin, ConversationPlugin
from dispatch.plugins.dispatch_slack.config import (
    SlackContactConfiguration,
    SlackConversationConfiguration,
)
from dispatch.signal.enums import SignalEngagementStatus
from dispatch.signal.models import SignalEngagement, SignalInstance

from .case.messages import (
    create_action_buttons_message,
    create_case_message,
    create_genai_signal_analysis_message,
    create_signal_engagement_message,
    create_signal_message,
)
from .endpoints import router as slack_event_router
from .enums import SlackAPIErrorCode
from .events import ChannelActivityEvent, ThreadActivityEvent
from .messaging import create_message_blocks
from .service import (
    add_conversation_bookmark,
    add_users_to_conversation,
    add_users_to_conversation_thread,
    archive_conversation,
    chunks,
    conversation_archived,
    create_conversation,
    create_slack_client,
    does_user_exist,
    emails_to_user_ids,
    get_channel_activity,
    get_user_avatar_url,
    get_user_info_by_id,
    get_user_profile_by_email,
    is_user,
    remove_member_from_channel,
    rename_conversation,
    resolve_user,
    send_ephemeral_message,
    send_message,
    set_conversation_description,
    set_conversation_topic,
    unarchive_conversation,
    update_message,
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
    plugin_events = [ChannelActivityEvent, ThreadActivityEvent]

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = SlackConversationConfiguration

    def create(self, name: str):
        """Creates a new Slack conversation."""
        client = create_slack_client(self.configuration)
        return create_conversation(client, name, self.configuration.private_channels)

    def create_threaded(self, case: Case, conversation_id: str, db_session: Session):
        """Creates a new threaded conversation."""
        client = create_slack_client(self.configuration)
        blocks = create_case_message(case=case, channel_id=conversation_id)
        response = send_message(client=client, conversation_id=conversation_id, blocks=blocks)
        response_timestamp = response["timestamp"]

        if case.signal_instances:
            signal_response = None

            # we try to generate a GenAI signal analysis message
            try:
                message, message_blocks = create_genai_signal_analysis_message(
                    case=case,
                    db_session=db_session,
                )
                if message and isinstance(message, dict):
                    # we update the genai_analysis field in the case model with the message if it's a dict
                    # if the message is a string, it means there was an error generating the analysis
                    case.genai_analysis = message

                if message_blocks:
                    signal_response = send_message(
                        client=client,
                        conversation_id=conversation_id,
                        ts=response_timestamp,
                        blocks=message_blocks,
                    )
            except Exception as e:
                logger.exception(f"Error generating GenAI signal analysis message: {e}")

            case.signal_thread_ts = (
                signal_response.get("timestamp") if signal_response else response_timestamp
            )

            # we try to generate a signal message
            try:
                message = create_signal_message(
                    case_id=case.id, channel_id=conversation_id, db_session=db_session
                )
                signal_response = send_message(
                    client=client,
                    conversation_id=conversation_id,
                    ts=case.signal_thread_ts,
                    blocks=message,
                )
                if signal_response:
                    case.signal_thread_ts = signal_response.get("timestamp")
            except Exception as e:
                logger.exception(f"Error generating signal message: {e}")

            # we try to upload the alert JSON to the case thread
            try:
                client.files_upload_v2(
                    channel=signal_response.get(
                        "id"
                    ),  # we need the conversation ID not the name here
                    thread_ts=case.signal_thread_ts,
                    file=io.BytesIO(json.dumps(case.signal_instances[0].raw, indent=4).encode()),
                )
            except SlackApiError as e:
                if e.response["error"] == SlackAPIErrorCode.MISSING_SCOPE:
                    exception_message = (
                        "Error uploading alert JSON to the case thread due to a missing scope"
                    )
                else:
                    exception_message = "Error uploading alert JSON to the case thread"
                logger.exception(f"{exception_message}: {e}")

            except Exception as e:
                logger.exception(f"Error uploading alert JSON to the case thread: {e}")

            # we try to generate action buttons
            try:
                message = create_action_buttons_message(
                    case=case, channel_id=conversation_id, db_session=db_session
                )
                send_message(
                    client=client,
                    conversation_id=conversation_id,
                    ts=case.signal_thread_ts,
                    blocks=message,
                )
            except Exception as e:
                logger.exception(f"Error generating action buttons message: {e}")

            db_session.commit()
        return response

    def create_engagement_threaded(
        self,
        case: Case,
        conversation_id: str,
        thread_id: str,
        user: DispatchUser,
        engagement: SignalEngagement,
        signal_instance: SignalInstance,
        engagement_status: SignalEngagementStatus = SignalEngagementStatus.new,
    ):
        """Creates a new engagement message."""
        client = create_slack_client(self.configuration)
        if not does_user_exist(client=client, email=user.email):
            not_found_msg = (
                f"Unable to engage user: {user.email}. User not found in the Slack workspace."
            )
            return send_message(
                client=client,
                conversation_id=conversation_id,
                text=not_found_msg,
                ts=thread_id,
            )

        blocks = create_signal_engagement_message(
            case=case,
            channel_id=conversation_id,
            user_email=user.email,
            engagement=engagement,
            signal_instance=signal_instance,
            engagement_status=engagement_status,
        )
        return send_message(
            client=client,
            conversation_id=conversation_id,
            blocks=blocks,
            ts=thread_id,
        )

    def update_thread(self, case: Case, conversation_id: str, ts: str):
        """Updates an existing threaded conversation."""
        client = create_slack_client(self.configuration)
        blocks = create_case_message(case=case, channel_id=conversation_id)
        return update_message(client=client, conversation_id=conversation_id, ts=ts, blocks=blocks)

    def update_signal_message(
        self,
        case_id: int,
        conversation_id: str,
        db_session: Session,
        thread_id: str,
    ):
        """Updates the signal message."""
        client = create_slack_client(self.configuration)
        blocks = create_signal_message(
            case_id=case_id, channel_id=conversation_id, db_session=db_session
        )
        return update_message(
            client=client, conversation_id=conversation_id, blocks=blocks, ts=thread_id
        )

    def send_message(self, conversation_id: str, blocks: list[Block]):
        """Updates an existing threaded conversation."""
        client = create_slack_client(self.configuration)
        return send_message(
            client=client,
            conversation_id=conversation_id,
            blocks=blocks,
        )

    def send(
        self,
        conversation_id: str,
        text: str,
        message_template: list[dict],
        notification_type: str,
        items: list | None = None,
        blocks: list | None = None,
        ts: str | None = None,
        persist: bool = False,
        **kwargs,
    ):
        """Sends a new message based on data and type."""
        try:
            client = create_slack_client(self.configuration)
            messages = []
            if not blocks:
                blocks = create_message_blocks(message_template, notification_type, items, **kwargs)

                for c in chunks(blocks, 50):
                    messages.append(
                        send_message(
                            client,
                            conversation_id,
                            text,
                            ts,
                            Message(blocks=c).build()["blocks"],
                            persist,
                        )
                    )
            else:
                for c in chunks(blocks, 50):
                    messages.append(send_message(client, conversation_id, text, ts, c, persist))
            return messages
        except SlackApiError as exception:
            error = exception.response["error"]
            if error == SlackAPIErrorCode.IS_ARCHIVED:
                # swallow send errors if the channel is archived
                message = f"SlackAPIError trying to send: {exception.response}. Message: {text}. Type: {notification_type}. Template: {message_template}"
                logger.error(message)
            else:
                raise exception

    def send_direct(
        self,
        user: str,
        text: str,
        message_template: dict,
        notification_type: str,
        items: list | None = None,
        ts: str | None = None,
        blocks: list | None = None,
        **kwargs,
    ):
        """Sends a message directly to a user if the user exists."""
        client = create_slack_client(self.configuration)
        if not does_user_exist(client, user):
            return {}
        user_id = resolve_user(client, user)["id"]

        if not blocks:
            blocks = Message(
                blocks=create_message_blocks(message_template, notification_type, items, **kwargs)
            ).build()["blocks"]

        return send_message(client, user_id, text, ts, blocks)

    def send_ephemeral(
        self,
        conversation_id: str,
        user: str,
        text: str,
        message_template: dict = None,
        notification_type: str = None,
        items: list | None = None,
        blocks: list | None = None,
        **kwargs,
    ):
        """Sends an ephemeral message to a user in a channel if the user exists."""
        client = create_slack_client(self.configuration)
        if not does_user_exist(client, user):
            return {}
        user_id = resolve_user(client, user)["id"]

        if not blocks:
            blocks = Message(
                blocks=create_message_blocks(message_template, notification_type, items, **kwargs)
            ).build()["blocks"]

        archived = conversation_archived(client, conversation_id)
        if not archived:
            send_ephemeral_message(client, conversation_id, user_id, text, blocks)

    def add(self, conversation_id: str, participants: list[str]):
        """Adds users to conversation if it is not archived."""
        client = create_slack_client(self.configuration)
        archived = conversation_archived(client, conversation_id)
        if not archived:
            participants = [resolve_user(client, p)["id"] for p in set(participants)]
            add_users_to_conversation(client, conversation_id, participants)

    def add_to_thread(self, conversation_id: str, thread_id: str, participants: list[str]):
        """Adds users to a thread conversation."""
        client = create_slack_client(self.configuration)
        user_ids = emails_to_user_ids(client=client, participants=participants)
        add_users_to_conversation_thread(client, conversation_id, thread_id, user_ids)

    def archive(self, conversation_id: str):
        """Archives a conversation."""
        client = create_slack_client(self.configuration)

        archived = conversation_archived(client, conversation_id)
        if not archived:
            archive_conversation(client, conversation_id)

    def unarchive(self, conversation_id: str):
        """Unarchives a conversation."""
        client = create_slack_client(self.configuration)
        return unarchive_conversation(client, conversation_id)

    def rename(self, conversation_id: str, name: str):
        """Renames a conversation."""
        client = create_slack_client(self.configuration)
        return rename_conversation(client, conversation_id, name)

    def get_participant_avatar_url(self, participant_id: str):
        """Gets the participant's avatar url."""
        client = create_slack_client(self.configuration)
        return get_user_avatar_url(client, participant_id)

    def set_topic(self, conversation_id: str, topic: str):
        """Sets the conversation topic."""
        client = create_slack_client(self.configuration)
        return set_conversation_topic(client, conversation_id, topic)

    def set_description(self, conversation_id: str, description: str):
        """Sets the conversation description."""
        client = create_slack_client(self.configuration)
        return set_conversation_description(client, conversation_id, description)

    def remove_user(self, conversation_id: str, user_email: str):
        """Removes a user from a conversation."""
        client = create_slack_client(self.configuration)
        user_id = resolve_user(client, user_email).get("id")
        if user_id:
            return remove_member_from_channel(
                client=client, conversation_id=conversation_id, user_id=user_id
            )

    def add_bookmark(self, conversation_id: str, weblink: str, title: str):
        """Adds a bookmark to the conversation."""
        client = create_slack_client(self.configuration)
        return add_conversation_bookmark(client, conversation_id, weblink, title)

    def get_command_name(self, command: str):
        """Gets the command name."""
        command_mappings = {
            ConversationCommands.assign_role: self.configuration.slack_command_assign_role,
            ConversationCommands.update_incident: self.configuration.slack_command_update_incident,
            ConversationCommands.engage_oncall: self.configuration.slack_command_engage_oncall,
            ConversationCommands.executive_report: self.configuration.slack_command_report_executive,
            ConversationCommands.list_participants: self.configuration.slack_command_list_participants,
            ConversationCommands.list_tasks: self.configuration.slack_command_list_tasks,
            ConversationCommands.tactical_report: self.configuration.slack_command_report_tactical,
            ConversationCommands.escalate_case: self.configuration.slack_command_escalate_case,
        }
        return command_mappings.get(command, [])

    def fetch_events(
        self, db_session: Session, subject: Any, plugin_event_id: int, oldest: str = "0", **kwargs
    ):
        """Fetches incident events from the Slack plugin.

        Args:
            subject: An Incident or Case object.
            plugin_event_id: The plugin event id.
            oldest: The oldest timestamp to fetch events from.

        Returns:
            A sorted list of tuples (utc_dt, user_id).
        """
        try:
            client = create_slack_client(self.configuration)
            plugin_event = plugin_service.get_plugin_event_by_id(
                db_session=db_session, plugin_event_id=plugin_event_id
            )
            event = self.get_event(plugin_event)
            if event is None:
                raise ValueError(f"No event found for Slack plugin event: {plugin_event}")

            event_instance = event()
            activity = event_instance.fetch_activity(client, subject, oldest)
            return activity
        except Exception as e:
            logger.exception(
                "An error occurred while fetching incident or case events from the Slack plugin.",
                exc_info=e,
            )
            raise

    def get_conversation(
        self, conversation_id: str, oldest: str = "0", include_user_details = False, important_reaction: str | None = None
    ) -> list:
        """
        Fetches the top-level posts from a Slack conversation.

        Args:
            conversation_id (str): The ID of the Slack conversation.
            oldest (str): The oldest timestamp to fetch messages from.
            include_user_details (bool): Whether to resolve user name and email information.
            important_reaction (str): Emoji reaction indicating important messages.

        Returns:
            list: A list of tuples containing the timestamp and user ID of each message.
        """
        client = create_slack_client(self.configuration)
        return get_channel_activity(
            client,
            conversation_id,
            oldest,
            include_message_text=True,
            include_user_details=include_user_details,
            important_reaction=important_reaction,
        )

    def get_conversation_replies(self, conversation_id: str, thread_ts: str) -> list[str]:
        """
        Fetches replies from a specific thread in a Slack conversation.

        Args:
            conversation_id (str): The ID of the Slack conversation.
            thread_ts (str): The timestamp of the thread to fetch replies from.

        Returns:
            list[str]: A list of replies from users in the specified thread.
        """
        client = create_slack_client(self.configuration)
        conversation_replies = client.conversations_replies(
            channel=conversation_id,
            ts=thread_ts,
        )["messages"]

        replies = []
        for reply in conversation_replies:
            if is_user(config=self.configuration, user_id=reply.get("user")):
                # we only include messages from users
                replies.append(f"{reply['text']}")
        return replies

    def get_all_member_emails(self, conversation_id: str) -> list[str]:
        """
        Fetches all members of a Slack conversation.

        Args:
            conversation_id (str): The ID of the Slack conversation.

        Returns:
            list[str]: A list of the emails for all members in the conversation.
        """
        client = create_slack_client(self.configuration)
        member_ids = client.conversations_members(channel=conversation_id).get("members", [])

        member_emails = []
        for member_id in member_ids:
            if is_user(config=self.configuration, user_id=member_id):
                user = get_user_info_by_id(client, member_id)
                if user and (profile := user.get("profile")) and (email := profile.get("email")):
                    member_emails.append(email)

        return member_emails


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
            weblink = str(
                profile_fields.get(self.configuration.profile_weblink_field_id, {}).get("value", "")
            )

        return {
            "fullname": profile["real_name"],
            # https://api.slack.com/methods/users.profile.get#email-addresses
            "email": profile.get("email", email),
            "title": profile["title"],
            "team": team,
            "department": department,
            "location": profile["tz"],
            "weblink": weblink,
            "thumbnail": profile["image_512"],
        }
