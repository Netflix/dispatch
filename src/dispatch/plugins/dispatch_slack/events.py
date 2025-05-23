import logging
from slack_sdk import WebClient

from dispatch.plugins.base import IPluginEvent

from .service import (
    get_channel_activity,
    get_thread_activity,
)

log = logging.getLogger(__name__)


class SlackPluginEvent(IPluginEvent):
    def fetch_activity(self):
        raise NotImplementedError


class ChannelActivityEvent(SlackPluginEvent):
    name = "Slack Channel Activity"
    slug = "slack-channel-activity"
    description = "Analyzes incident/case activity within a specific Slack channel.\n \
        By periodically polling channel messages, this gathers insights into the \
        activity and engagement levels of each participant."

    def fetch_activity(self, client: WebClient, subject: None, oldest: str = "0") -> list:
        if not subject:
            log.warning("No subject provided. Cannot fetch channel activity.")
        elif not subject.conversation:
            log.info("No conversation provided. Cannot fetch channel activity.")
        elif not subject.conversation.channel_id:
            log.info("No channel id provided. Cannot fetch channel activity.")
        elif subject.conversation.thread_id:
            log.info(
                "Subject is a thread, not a channel. Fetching channel activity is not applicable for threads."
            )
        else:
            return get_channel_activity(
                client, conversation_id=subject.conversation.channel_id, oldest=oldest
            )
        return []


class ThreadActivityEvent(SlackPluginEvent):
    name = "Slack Thread Activity"
    slug = "slack-thread-activity"
    description = "Analyzes incident/case activity within a specific Slack thread.\n \
        By periodically polling thread replies, this gathers insights \
        into the activity and engagement levels of each participant."

    def fetch_activity(self, client: WebClient, subject: None, oldest: str = "0") -> list:
        if not subject:
            log.warning("No subject provided. Cannot fetch thread activity.")
        elif not subject.conversation:
            log.info("No conversation provided. Cannot fetch thread activity.")
        elif not subject.conversation.channel_id:
            log.info("No channel id provided. Cannot fetch thread activity.")
        elif not subject.conversation.thread_id:
            log.info("No thread id provided. Cannot fetch thread activity.")
        else:
            return get_thread_activity(
                client,
                conversation_id=subject.conversation.channel_id,
                ts=subject.conversation.thread_id,
                oldest=oldest,
            )
        return []
