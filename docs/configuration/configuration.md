# Configuring Dispatch

okThis document describes additional configuration options available for the Dispatch server itself. Additional plugin specific configuration can be found in the plugin's documentation.

## First Install

Dispatch uses the same configuration system as [Starlette](https://www.starlette.io/config/).

By default, the config will be read from environment variables and/or `.env` files.

### General

#### `LOG_LEVEL` \[default: 'warning'\]

> Controls the level of logging the application will perform during operations.

#### `STATIC_DIR` \[default: './src/static/dispatch/dist'\]

> Controls where static content for the Dispatch Web UI should be served from. This can also be explicitly set to `''` if you wish to serve static content outside of the Dispatch server.

#### `METRIC_PROVIDERS` \[default: ""\]

> A comma separated list of metric providers Dispatch will send key system metrics to.

#### `SENTRY_DSN` \[default: none\]

> Optional configuration for using Sentry to report Dispatch errors.

#### `DISPATCH_HELP_EMAIL`

> Email address to be used by Dispatch when a help message is created.

#### `DISPATCH_HELP_SLACK_CHANNEL`

> Slack channel name to be used by Dispatch when a help message is created.

### Authentication

#### `JWKS_URL`

> Used by Dispatch's authentication backend to pull the JSON Web Key Set \(JWKS\) public key from our specified provider. The result of this URL is cached for up to 1 hour.

#### `VUE_APP_DISPATCH_OPEN_ID_CONNECT_URL`

> Used by the Dispatch Web UI send the user via Proof Key Code Exchange \(PKCE\) to a correct open id connect endpoint.
> Configuration located at: `/src/dispatch/static/dispatch/.env` 

#### `VUE_APP_DISPATCH_CLIENT_ID`

> The client id to send to the open id connect endpoint.
> Configuration located at: `/src/dispatch/static/dispatch/.env` 

### Persistence

#### `DATABASE_HOSTNAME`

> Dispatch relies on a `Postgres` database. This host name should point to a supporter version of `Postgres (9.6+)`.

#### `DATABASE_CREDENTIALS`

> Credentials specified in `username:password` format to be used to authenticate to the `postgres` database.

#### `DATABASE_NAME` \[default: 'dispatch'\]

> Allows the user to specify the database name for the `Dispatch` backend.

#### `DATABASE_PORT` \[default: '5432'\]

> Allows the user to specify the database port for the `Dispatch` backend.

### Models

### Incident Cost

#### `ANNUAL_COST_EMPLOYEE` \[default: '650000'\]

> Used for incident cost modeling, specifies the total `all-in` cost for an average employee working on incidents.

#### `BUSINESS_HOURS_YEAR` \[default: '2080'\]

> Used for incident cost modeling, specifies the number of hours in an employee's work week.

### Incident Plugin Configuration

#### `INCIDENT_PLUGIN_CONTACT_SLUG` \[default: 'pandora-contact'\]

> Controls which plugin will be used to resolve incident participant email addresses. The plugin will also be used to gather additional participant information such as name, team, location, etc.

#### `INCIDENT_PLUGIN_CONVERSATION_SLUG` \[default: 'slack-conversation'\]

> Controls which plugin will be used for incident conversations.

#### `INCIDENT_PLUGIN_DOCUMENT_SLUG` \[default: 'google-docs-document'\]

> Controls which plugin will be used for incident document creation.

#### \`INCIDENT\_PLUGIN\_DOCUMENT\_RESOLVER\_SLUG \[default: 'dispatch-document-resolver'\]

> Controls which plugin will be used to recommend documents to be automatically included for a given incident.

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

#### `INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID`

> Controls the folder where to archive incident information.

#### `INCIDENT_NOTIFICATION_CONVERSATIONS` \[default: ''\]

> Comma separated list of conversations \(e.g. Slack channels\) to be notified of new incidents.

#### `INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS` \[default: ''\]

> Comma separated list of email addresses to be notified of new incidents.

#### `INCIDENT_DAILY_SUMMARY_ONCALL_SERVICE_ID` \[default: None\]

> Specifies the oncall service id to use to resolve the oncall person that is included in the daily incidents summary.

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

