import os
import pandas as pd
from slack_sdk import WebClient
from collections import defaultdict
from typing import List, Optional

from dispatch.plugins.base import IPluginEvent
from dispatch.plugin.models import PluginEvent

from .service import (
    get_channel_messages,
    get_thread_replies,
)


class SlackPluginEvent(IPluginEvent):
    def fetch_activity(self):
        raise NotImplementedError


class ChannelActivityEvent(IPluginEvent):
    name = "fetch-channel-messages"
    description = "Fetches channel messages"

    def fetch_activity(client: WebClient, subject: None, exclusions=List):
        print("fetch-channel-messages")
        return get_channel_messages(
            client, conversation_id=subject.conversation.channel_id, exclusions=exclusions
        )


class ThreadActivityEvent(IPluginEvent):
    name = "fetch-thread-replies"
    description = "Fetches thread replies"

    def fetch_activity(client: WebClient, subject: None, exclusions=List):
        print("fetch-thread-replies")
        return get_thread_replies(
            client,
            conversation_id=subject.conversation.channel_id,
            ts=subject.conversation.thread_id,
            exclusions=exclusions,
        )


def record_thread_activity(
    client: WebClient, channel: str, ts: str, user_activity: defaultdict
) -> int:
    has_more = True
    cursor = None
    while has_more:
        thread_history = client.conversations_replies(
            channel=channel, ts=ts, cursor=cursor
        )  # assume we do not have more than 1000 replies
        if thread_history["ok"] and "messages" in thread_history:
            has_more = thread_history["has_more"]
            if has_more:
                cursor = thread_history["response_metadata"]["next_cursor"]
            for message in thread_history["messages"]:
                if not "user" in message:
                    print(f"Error retrieving message for thread {ts}")
                    continue
                user_activity[message["user"]] += [float(message["ts"])]


def get_slack_history(client: WebClient, channel: str, user_activity: defaultdict) -> dict:
    has_more = True
    total_messages = 0
    total_threads = 0
    cursor = None
    while has_more:
        history = client.conversations_history(channel=channel, cursor=cursor, limit=100)
        if history["ok"]:
            if not "messages" in history:
                return

            # for large limits
            has_more = history["has_more"]
            if has_more:
                cursor = history["response_metadata"]["next_cursor"]

            for message in history["messages"]:
                # filter out channel joined messages and bot messages
                if (
                    "subtype" in message
                    and message["subtype"] == "channel_join"
                    or message["subtype"] == "bot_message"
                ):
                    continue

                if not "user" in message:
                    print(f"Error retrieving message {message}")
                    continue
                total_messages += 1
                user_activity[message["user"]] += [float(message["ts"])]

                # check for thread activity
                if "reply_count" in message:
                    total_threads += message["reply_count"]
                    record_thread_activity(
                        client, channel, ts=message["thread_ts"], user_activity=user_activity
                    )
        print(f"messages: {total_messages}")
        print(f"thread activity: {total_threads}")
