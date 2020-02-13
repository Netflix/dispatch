# Configuring Slack

By default, Dispatch ships with support for Slack via it's `Slack` plugin. Below you'll find on how to configure the slack plugin to work with `Dispatch`.

Note: The `slack` plugin relies on the events API to recieve commands and messages from Slack. It recieves these messages by advertising a /events endpoint off of the `Dispatch` api. This endpoint must be publically available in order for the `Dispatch` slack app to work correctly.

## Configuration

#### `SLACK_APP_USER_SLUG`

> Specifies the slack app id so Dispatch can filter events from the app.

#### `SLACK_WORKSPACE_NAME`

> Specifies the name of the workspace the slack app is installed in.

#### `SLACK_API_BOT_TOKEN` [secret: True]

> Token used to communicate with the slack api.

#### `SLACK_SIGNING_SECRET` [secret: True]

> Token used to verify events are sent from Slack itself.

#### `SLACK_USER_ID_OVERRIDE` [default: None]

> Used during development to funnel all resolved messages to a particular user.

#### `SLACK_COMMAND_MARK_ACTIVE_SLUG` [default: '/dispatch-mark-active']

> Active command as displayed in Slack>

#### `SLACK_COMMAND_MARK_STABLE_SLUG` [default: '/dispatch-mark-stable']

> Stable command as displayed in Slack.

#### `SLACK_COMMAND_MARK_CLOSED_SLUG` [default: '/dispatch-mark-closed']

> Close command as displayed in Slack.

#### `SLACK_COMMAND_STATUS_REPORT_SLUG` [default: '/dispatch-status-report']

> Status report command as displayed in Slack.

#### `SLACK_COMMAND_LIST_TASKS_SLUG` [default: '/dispatch-list-tasks']

> List tasks command as displayed in Slack.

#### `SLACK_COMMAND_LIST_PARTICIPANTS_SLUG` [default: '/dispatch-list-participants']

> List participants command as displayed in Slack.

#### `SLACK_COMMAND_ASSIGN_ROLE` [default: '/dispatch-assign-role']

> Assign role command as displayed in Slack.

#### `SLACK_COMMAND_EDIT_INCIDENT` [default: '/dispatch-edit-incident']

> Edit incident command as displayed in Slack.

#### `SLACK_COMMAND_ENGAGE_ONCALL` [default: '/dispatch-engage-oncall']

> Engage oncall command as displayed in Slack.

#### `SLACK_COMMAND_LIST_RESOURCES` [default: `/dispatch-list-resources']

> List resources command as displayed in Slack.

## Commands

To enable Dispatch's slash commands you must create them an point them to the approriate endpoint:

![commands0](../../images/slack-setup-commands-0.png)

![commands1](../../images/slack-setup-commands-1.png)

Ensure that the `Command` matches the configuration variables above and that `Request URL` points to the events endpoint of the dispatch server (`/api/v1/events/slack/command`).

## Events

To enable Dispatch to process slack events ensure you configuration looks similar to the following:

![events0](../../images/slack-setup-events.png)

## Dialogs

To enable Dispatch Dialogs ensure your configuration looks similar to the following:

![dialogs0](../../images/slack-setup-dialogs.png)

## Permissions

In addition you will have to ensure that the `Dispatch` will has the following access for your workspace:

### OAuth Scopes

The following are the scopes required for the Dispatch Slack App to function correctly.

#### Bot Scopes

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

#### User Scopes

    channels:read
    groups:history
    groups:read
