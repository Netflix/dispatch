import logging
from slack_sdk import WebClient
from typing import List

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

    def fetch_activity(client: WebClient, subject: None, oldest: str = "0") -> List:
        if not subject:
            log.warning("No subject provided. Cannot fetch channel activity.")
        elif not subject.conversation:
            log.warning("No conversation provided. Cannot fetch channel activity.")
        elif not subject.conversation.channel_id:
            log.warning("No channel id provided. Cannot fetch channel activity.")
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

    def fetch_activity(client: WebClient, subject: None, oldest: str = "0") -> List:
        if not subject:
            log.warning("No subject provided. Cannot fetch thread activity.")
        elif not subject.conversation:
            log.warning("No conversation provided. Cannot fetch thread activity.")
        elif not subject.conversation.channel_id:
            log.warning("No channel id provided. Cannot fetch thread activity.")
        elif not subject.conversation.thread_id:
            log.warning("No thread id provided. Cannot fetch thread activity.")
        else:
            return get_thread_activity(
                client,
                conversation_id=subject.conversation.channel_id,
                ts=subject.conversation.thread_id,
                oldest=oldest,
            )
        return []
