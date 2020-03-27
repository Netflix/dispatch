---
description: Configuration for Slack plugin.
---

# Configuring Slack

By default, Dispatch ships with support for Slack. Below, is how to configure the slack plugin to work with `Dispatch`.

{% hint style="info" %}
The `Slack` plugin relies on the [Events API](https://api.slack.com/events-api) to receive events for the event types the bot is subscribed to. `Dispatch` receives these events at the `/events/slack/event` API endpoint. This endpoint must be publicly available in order for the `Dispatch` Slack app to work correctly.
{% endhint %}

## Configuration

#### `SLACK_APP_USER_SLUG`

> Specifies the Slack app id so Dispatch can filter events from the app.

#### `SLACK_WORKSPACE_NAME`

> Specifies the name of the workspace the Slack app is installed in.

#### `SLACK_API_BOT_TOKEN` \[secret: True\]

> Bot Token used to communicate with the Slack API.

#### `SLACK_SIGNING_SECRET` \[secret: True\]

> Secret used to verify signatures included on each HTTP request that Slack sends.

#### `SLACK_USER_ID_OVERRIDE` \[default: None\]

> Used during development to funnel all messages to a particular user.

#### `SLACK_COMMAND_MARK_ACTIVE_SLUG` \[default: '/dispatch-mark-active'\] \[DEPRECATED\]

> Active command as displayed in Slack.

#### `SLACK_COMMAND_MARK_STABLE_SLUG` \[default: '/dispatch-mark-stable'\] \[DEPRECATED\]

> Stable command as displayed in Slack.

#### `SLACK_COMMAND_MARK_CLOSED_SLUG` \[default: '/dispatch-mark-closed'\] \[DEPRECATED\]

> Close command as displayed in Slack.

#### `SLACK_COMMAND_STATUS_REPORT_SLUG` \[default: '/dispatch-status-report'\]

> Status report command as displayed in Slack.

#### `SLACK_COMMAND_LIST_TASKS_SLUG` \[default: '/dispatch-list-tasks'\]

> List tasks command as displayed in Slack.

#### `SLACK_COMMAND_LIST_PARTICIPANTS_SLUG` \[default: '/dispatch-list-participants'\]

> List participants command as displayed in Slack.

#### `SLACK_COMMAND_ASSIGN_ROLE` \[default: '/dispatch-assign-role'\]

> Assign role command as displayed in Slack.

#### `SLACK_COMMAND_UPDATE_INCIDENT` \[default: '/dispatch-update-incident'\]

> Update incident command as displayed in Slack.

#### `SLACK_COMMAND_ENGAGE_ONCALL` \[default: '/dispatch-engage-oncall'\]

> Engage oncall command as displayed in Slack.

#### `SLACK_COMMAND_LIST_RESOURCES` \[default: \`/dispatch-list-resources'\]

> List resources command as displayed in Slack.

## Commands

To enable Dispatch's slash commands you must create them an point them to the appropriate endpoint:

![](../../.gitbook/assets/slack-setup-commands-0%20%281%29.png)

![](../../.gitbook/assets/slack-setup-commands-1.png)

Ensure that the `Command` matches the configuration variables above and that `Request URL` points to the events endpoint of the dispatch server \(`/api/v1/events/slack/command`\).

## Events

To enable Dispatch to process slack events ensure you configuration looks similar to the following:

![](../../.gitbook/assets/slack-setup-events%20%281%29.png)

## Dialogs

To enable Dispatch Dialogs ensure your configuration looks similar to the following:

![](../../.gitbook/assets/slack-setup-dialogs.png)

## Permissions

### OAuth Scopes

The following are the scopes required for the Dispatch Slack App to function correctly.

#### Bot Scopes

```text
channels:read
chat:write
commands
files:read
groups:history
groups:read
groups:write
im:history
im:read
im:write
mpim:history
mpim:read
mpim:write
pins:write
reactions:read
reactions:write
reminders:write
remote_files:read
team:read
users:read
users:read.email
users:write
```

#### User Scopes

```text
channels:read
groups:history
groups:read
```

