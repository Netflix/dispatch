from datetime import datetime
from slack_sdk import WebClient
from typing import Any

from dispatch.plugins.bases import ConversationPlugin
from dispatch.plugins.dispatch_slack.events import ChannelActivityEvent


class TestWebClient(WebClient):
    def api_call(self, *args, **kwargs):
        return {"ok": True, "messages": [], "has_more": False}


class TestConversationPlugin(ConversationPlugin):
    id = 123
    title = "Dispatch Test Plugin - Conversation"
    slug = "test-conversation"
    configuration = {"api_bot_token": "123"}
    type = "conversation"
    plugin_events = [ChannelActivityEvent]

    def create(self, items, **kwargs):
        return

    def add(self, items, **kwargs):
        return

    def send(self, items, **kwargs):
        return

    def fetch_incident_events(self, subject: Any, **kwargs):
        client = TestWebClient()
        for plugin_event in self.plugin_events:
            plugin_event.fetch_activity(client=client, subject=subject)
        return [
            (datetime.utcfromtimestamp(1512085950.000216), "0XDECAFBAD"),
            (datetime.utcfromtimestamp(1512104434.000490), "0XDECAFBAD"),
            (datetime.utcfromtimestamp(1512104534.000490), "0X8BADF00D"),
        ]
