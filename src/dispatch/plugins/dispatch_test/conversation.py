from typing import Any

from slack_sdk import WebClient
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
        print("fetching incident events")
        print(self.plugin_events)
        client = TestWebClient()
        for event in self.plugin_events:
            event.fetch_activity(client=client, subject=subject, exclusions=[])
        return {
            "id": "123456",
            "messages": [
                {
                    "type": "message",
                    "user": "U123ABC456",
                    "text": "I find you punny and would like to smell your nose letter",
                    "ts": "1512085950.000216",
                },
                {
                    "type": "message",
                    "user": "U222BBB222",
                    "text": "What, you want to smell my shoes better?",
                    "ts": "1512104434.000490",
                },
            ],
        }
