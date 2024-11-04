from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.config import SlackConversationConfiguration
from dispatch.plugins.dispatch_slack.middleware import db_middleware

from .list import handle_list_signals_command


def configure(config: SlackConversationConfiguration):
    """Maps commands/events to their functions."""

    app.command(config.slack_command_list_signals, middleware=[db_middleware])(
        handle_list_signals_command
    )
