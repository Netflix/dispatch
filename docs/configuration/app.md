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
All config items prefixed with `VUE_APP` are envvars for the Vue frontend. These variables are used only during the building of the javascript bundle. See [here](https://cli.vuejs.org/guide/mode-and-env.html) for details. You will want to include these variables in `src/dispatch/static/dispatch/.env` during build time.
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

#### `SECRET_PROVIDER` \[default: None\]

> Defines the provider to use for configuration secret decryption. Available options are: `kms-secret` and `metatron-secret`

#### `ENV_TAGS` \[defaut: ""\]

> A comma separated list of tags that Dispatch will attempt to pull from the environment. As an example the string `foo:bar,baz:blah` will create two tags: `foo` with the environment value for `bar` and `baz` with the environment value for `blah`.

#### `SENTRY_DSN` \[default: none\]

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

#### `DISPATCH_JWT_ALG` \['default': 'HS256'\]

> Used by the basic auth provider to mint JWT tokens.

#### `DISPATCH_JWT_EXP` \['default': 86400 \]

> Used by the basic auth provider to mint JWT tokens and set their expiration.

#### `DISPATCH_JWT_AUDIENCE`

> Override what the `Audience` is expected to be in the PKCE JWT decode

#### `DISPATCH_JWT_EMAIL_OVERRIDE`

> Override where Dispatch should find the user email in the idtoken.

#### `DISPATCH_AUTHENTICATION_DEFAULT_USER` \['default': dispatch@example.com\]

> Used as the default anonymous user when authentication is disabled.

#### Configuration for `dispatch-auth-provider-pkce`

{% hint style="warning" %}
In order for this plugin to work with your OIDC setup, you may need to set 
`DISPATCH_JWT_AUDIENCE` and `DISPATCH_PKCE_DONT_VERIFY_AT_HASH`. 
{% endhint %}

#### `DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWK` \['default': true\]

> Used by Dispatch's authentication backend to pull the JSON Web Key Set \(JWKS\) public key from the specified provider. 
> This will likely be the `jwks_uri` URL from your OIDC provider.

#### `DISPATCH_PKCE_DONT_VERIFY_AT_HASH` \['default': false\]

> Depending on what values your OIDC provider sends, you may need to set this to `true` for the Dispatch backend
> to be able to decode the JWT token.

#### `VUE_APP_DISPATCH_AUTHENTICATION_PROVIDER_PKCE_OPEN_ID_CONNECT_URL`

> The well-known configuration URL for your OIDC provider, without a trailing slash. Used by the Dispatch 
> Web UI to authenticate a user via Proof Key Code Exchange \(PKCE\).

#### `VUE_APP_DISPATCH_AUTHENTICATION_PROVIDER_PKCE_CLIENT_ID`

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

Dispatch [calculates](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/service.py#L279) the cost of an incident by adding up the time participants have spent on each incident role \(e.g. Incident Commander\) and applying an [engagement multiplier](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/service.py#L266) that's based on the incident role. It also includes time spent on incident review related activities. Dispatch calculates and published the cost for all incidents [every 5 minutes](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/scheduled.py#L257).

#### `ANNUAL_COST_EMPLOYEE` \[default: '50000'\]

> Used for incident cost modeling, specifies the total `all-in` average cost for an employee working on incidents.

#### `BUSINESS_HOURS_YEAR` \[default: '2080'\]

> Used for incident cost modeling, specifies the number of hours in an employee's work year.

### Incident Resource Configuration

#### `INCIDENT_STORAGE_FOLDER_ID`

> Top level folder where all incident data is stored. Note: viewing actual incident data is still on a per-sub folder basis. For Google Drive,
> you can get the folder ID from viewing a folder in the Google Drive UI, and copying the last part of the URL (`/drive/u/0/folders/<this value>`)

#### `INCIDENT_STORAGE_OPEN_ON_CLOSE` \[default: 'true'\]

> After an incident is closed, Netflix as an organization, tries to be transparent and allow others within the organization to view incident data. This is may not desirable in all organizations. This controls whether to open up incident data on incident close.

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
