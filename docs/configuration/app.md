---
description: >-
  Describes additional configuration options available for the Dispatch server
  itself. Additional plugin-specific configuration can be found in the plugin's
  documentation.
---

# App

## First Install

Dispatch uses the same configuration system as [Starlette](https://www.starlette.io/config/).

By default, the config will be read from environment variables and/or `.env` files.

{% hint style="info" %}
All config items prefixed with `VUE_APP` are envvars for the Vue frontend. These variables are used only during the building of the javascript bundle. See [here](https://cli.vuejs.org/guide/mode-and-env.html) for details.
{% endhint %}

{% hint style="info" %}
In general, do not include any quotation marks when adding configuration values.
{% endhint %}

### General

#### `LOG_LEVEL` \[default: 'warning'\]

> Controls the level of logging the application will perform during operations.

#### `STATIC_DIR` \[default: './src/static/dispatch/dist'\]

> Controls where static content for the Dispatch Web UI should be served from. This can also be explicitly set to `''` if you wish to serve static content outside of the Dispatch server.

#### `METRIC_PROVIDERS` \[default: ""\]

> A comma separated list of metric providers Dispatch will send key system metrics to.

#### `SENTRY_DSN` \[default: none\] \[secret: True\]

> Optional configuration for using Sentry to report Dispatch errors.

#### `VUE_APP_SENTRY_DSN` \[default: none\]

> Optional configuration for using Sentry to report Dispatch errors.

#### `DISPATCH_HELP_EMAIL`

> Email address to be used by Dispatch when a help message is created.

#### `DISPATCH_HELP_SLACK_CHANNEL`

> Slack channel name to be used by Dispatch when a help message is created.

#### `DISPATCH_UI_URL`

> URL being used for Dispatch's Admin UI. Used in messaging to refer to the Admin UI.

### Authentication

#### `DISPATCH_AUTHENTICATION_PROVIDER_SLUG` \['default': dispatch-auth-provider-basic\]

> Used by Dispatch to determine which authentication provider to use, by default Dispatch ships with a PKCE authentication provider.

{% hint style="info" %}
If you wish to disable authentication set `DISPATCH_AUTHENTICATION_PROVIDER_SLUG=`
{% endhint %}

#### Configuration for `dispatch-auth-provider-basic`

{% hint style="warning" %}
Today, basic authentication allows self registration without approval.
{% endhint %}

{% hint style="warning" %}
In order for this plugin to work, you need to set `DISPATCH_JWT_SECRET`.
{% endhint %}

#### `DISPATCH_JWT_SECRET`

> Used by the basic auth provider to mint JWT tokens.

#### `DISPATCH_JWT_ALG` ['default': 'HS256']

> Used by the basic auth provider to mint JWT tokens.

#### `DISPATCH_JWT_EXP` ['default': 86400 ]

> Used by the basic auth provider to mint JWT tokens and set their expiration.

#### `DISPATCH_JWT_AUDIENCE`

> Override what the `Audience` is expected to be in the PKCE JWT decode

#### `DISPATCH_JWT_EMAIL_OVERRIDE`

> Override where Dispatch should find the user email in the idtoken.

#### `DISPATCH_AUTHENTICATION_DEFAULT_USER` \['default': dispatch@example.com\]

> Used as the default anonymous user when authentication is disabled.

#### Configuration for `dispatch-auth-provider-pkce`

#### `DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWK` \['default': true\]

> Used by Dispatch's authentication backend to pull the JSON Web Key Set \(JWKS\) public key from the specified provider.

#### `VUE_APP_DISPATCH_AUTHENTICATION_PROVIDER_PKCE_OPEN_ID_CONNECT`

> Used by the Dispatch Web UI send the user via Proof Key Code Exchange \(PKCE\) to a correct OpenID Connect endpoint.

#### `VUE_APP_DISPATCH_AUTHENTICATOIN_PROVIDER_PKCE_CLIENT_ID`

> The client id to send to the OpenID Connect endpoint.

### Persistence

#### `DATABASE_HOSTNAME`

> Dispatch relies on a `Postgres` database. This host name should point to a supporter version of `Postgres (9.6+)`.

#### `DATABASE_CREDENTIALS` \[secret: True\]

> Credentials specified in `username:password` format to be used to authenticate to the `postgres` database.

#### `DATABASE_NAME` \[default: 'dispatch'\]

> Allows the user to specify the database name for the `Dispatch` backend.

#### `DATABASE_PORT` \[default: '5432'\]

> Allows the user to specify the database port for the `Dispatch` backend.

### Models

### Incident Cost

Dispatch [calculates](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/service.py#L279) the cost of an incident by adding up the time participants have spent on each incident role (e.g. Incident Commander) and applying an [engagement multiplier](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/service.py#L266) that's based on the incident role. It also includes time spent on incident review related activities. Dispatch calculates and published the cost for all incidents [every 5 minutes](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/scheduled.py#L257).

#### `ANNUAL_COST_EMPLOYEE` \[default: '50000'\]

> Used for incident cost modeling, specifies the total `all-in` average cost for an employee working on incidents.

#### `BUSINESS_HOURS_YEAR` \[default: '2080'\]

> Used for incident cost modeling, specifies the number of hours in an employee's work year.

### Incident Plugin Configuration

#### `INCIDENT_PLUGIN_CONTACT_SLUG` \[default: 'slack-contact'\]

> Controls which plugin will be used to resolve incident participant email addresses. The plugin will also be used to gather additional participant information such as name, team, location, etc.

#### `INCIDENT_PLUGIN_CONVERSATION_SLUG` \[default: 'slack-conversation'\]

> Controls which plugin will be used for incident conversations.

#### `INCIDENT_PLUGIN_DOCUMENT_SLUG` \[default: 'google-docs-document'\]

> Controls which plugin will be used for incident document creation.

#### `INCIDENT_PLUGIN_DOCUMENT_RESOLVER_SLUG` \[default: 'dispatch-document-resolver'\]

> Controls which plugin will be used to recommend documents to be automatically included for a given incident.

#### `INCIDENT_PLUGIN_CONFERENCE_PLUGIN` \[default: 'google-calendar-conference'\]

> Controls which plugin will be used to create a conference.

#### `INCIDENT_PLUGIN_EMAIL_SLUG` \[default: 'google-gmail-conversation'\]

> Controls which plugin will be used to send incident email notifications.

#### `INCIDENT_PLUGIN_GROUP_SLUG` \[default: 'google-group-participant-group'\]

> Controls which plugin will be used to create incident participant groups \(DLs\).

#### `INCIDENT_PLUGIN_PARTICIPANT_SLUG` \[default: 'dispatch-participants'\]

> Controls which plugin will be used to determine which participants should be automatically included for a given incident.

#### `INCIDENT_PLUGIN_STORAGE_SLUG` \[default: 'google-drive-storage'\]

> Controls which plugin will be used for incident storage.

#### `INCIDENT_PLUGIN_TICKET_SLUG` \[default: 'jira-ticket'\]

> Controls the plugin to use for creating external tickets. The ticket number is used as incident name.

#### `INCIDENT_PLUGIN_TASK_SLUG` \[default: 'google-drive-task'\]

> Controls the plugin to use for creation of incident tasks.

### Incident Resource Configuration

#### `INCIDENT_FAQ_DOCUMENT_ID`

> Controls which document id to use as the FAQ.

#### `INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT_ID`

> Controls which document id to use for the conversation commands reference document.

#### `INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID`

> Controls the folder where to archive incident information.

#### `INCIDENT_STORAGE_RESTRICTED` \[default: 'True'\]

> Controls whether a set of restrictions and capabilities to prevent content sharing need to be applied.

#### `INCIDENT_NOTIFICATION_CONVERSATIONS` \[default: ''\]

> Comma separated list of conversations \(e.g. Slack channels\) to be notified of new incidents.

#### `INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS` \[default: ''\]

> Comma separated list of email addresses to be notified of new incidents.

#### `INCIDENT_ONCALL_SERVICE_ID` \[default: None\]

> Specifies the oncall service id to use to resolve the oncall person.

#### `INCIDENT_RESOURCE_TASK` \[default: 'google-docs-incident-task'\]

> Controls the resource type to use for incident tasks.

#### `INCIDENT_RESOURCE_FAQ_DOCUMENT` \[default: 'google-docs-faq-document'\]

> Controls the resource type to use for the incident faq document.

#### `INCIDENT_RESOURCE_TACTICAL_GROUP` \[default: 'google-group-participant-tactical-group'\]

> Controls the resource type to use for tactical groups.

#### `INCIDENT_RESOURCE_NOTIFICATIONS_GROUP` \[default: 'google-group-participant-notification-group'\]

> Controls the resource type to use for notification groups.

#### `INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT` \[default: 'google-docs-investigation-document'\]

> Controls the resource type to use for the investigation document.

#### `INCIDENT_RESOURCE_INVESTIGATION_SHEET` \[default: 'google-docs-investigation-sheet'\]

> Controls the resource type to use for the investigation sheet.

#### `INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT` \[default: 'google-docs-incident-review-document'\]

> Controls the resource type to use for the incident review document.
