---
description: >-
  Describes additional configuration options available for the Dispatch server
  itself. Additional plugin-specific configuration can be found in the plugin's
  documentation.
---

## First Install

Dispatch uses the same configuration system as [Starlette](https://www.starlette.io/config/).

By default, the config is read from environment variables or `.env` files.

{% hint style="info" %}
All config items prefixed with `VITE_` are envvars for the Vue frontend. These variables are used only during the building of the javascript bundle. See [here](https://vitejs.dev/guide/env-and-mode.html) for details. You will want to include these variables in `src/dispatch/static/dispatch/.env` during build time.
{% endhint %}

{% hint style="info" %}
In general, do not include any quotation marks when adding configuration values.
{% endhint %}

### General

#### `LOG_LEVEL` \[default: 'WARNING'\]

> Controls the level of logging the application will perform during operations. Possible values: CRITICAL, ERROR, WARNING, INFO, DEBUG

#### `STATIC_DIR` \[default: './src/static/dispatch/dist'\]

> Controls where on the local disk, static content for the Dispatch Web UI should be served. This variable can also be explicitly set to `''` if you wish to serve static content outside of the Dispatch server.

#### `METRIC_PROVIDERS` \[default: ""\]

> A comma-separated list of metric providers where Dispatch will send key system metrics.

#### `SECRET_PROVIDER` \[default: None\]

> Defines the provider to use for configuration secret decryption. Available options are: `kms-secret` and `metatron-secret`

#### `ENV_TAGS` \[default: ""\]

> A comma-separated list of tags that Dispatch will attempt to pull from the environment. For example, the string `foo:bar,baz:blah` will create two tags: `foo` with the environment value for `bar` and `baz` with the environment value for `blah`.

#### `SENTRY_DSN` \[default: none\]

> Optional configuration for using Sentry to report Dispatch errors.

#### `MJML_PATH` \[default: /node_modules/.bin]

> Dispatch uses [MJML](https://mjml.io/documentation/) to generate its HTML emails. This package also requires the `node` binary to be available on the standard path (or set in Dispatch's path). Use this variable to adjust the location where Dispatch should look for the `mjml` command. **If you are using the stock docker image of Dispatch you must manually set this field to the default path.**

#### `DISPATCH_UI_URL`

> URL of the Dispatch's Admin UI, used by messaging to refer to the Admin UI.

### Authentication

#### `DISPATCH_AUTHENTICATION_PROVIDER_SLUG` \['default': dispatch-auth-provider-basic\]

> Used by Dispatch to determine which authentication provider to use; by default, Dispatch ships with a PKCE authentication provider.

{% hint style="info" %}
If you wish to disable authentication set `DISPATCH_AUTHENTICATION_PROVIDER_SLUG=`
{% endhint %}

#### Configuration for `dispatch-auth-provider-basic`

{% hint style="warning" %}
Today, basic authentication allows self-registration without approval.
{% endhint %}

{% hint style="warning" %}
For this plugin to work, you need to set `DISPATCH_JWT_SECRET`.
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
For this plugin to work with your OIDC setup, you may need to set
`DISPATCH_JWT_AUDIENCE` and `DISPATCH_PKCE_DONT_VERIFY_AT_HASH`.
{% endhint %}

#### `DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS`

> Used by Dispatch's authentication backend to pull the JSON Web Key Set \(JWKS\) public key from the specified provider.
> This will likely be the `jwks_uri` URL from your OIDC provider.
> This is required when using the `dispatch-auth-provider-pkce` auth provider.

#### `DISPATCH_PKCE_DONT_VERIFY_AT_HASH` \['default': false\]

> Depending on what values your OIDC provider sends, you may need to set this to `true` for the Dispatch backend
> to be able to decode the JWT token.

#### `DISPATCH_AUTHENTICATION_PROVIDER_PKCE_OPEN_ID_CONNECT_URL`

> The well-known configuration URL for your OIDC provider, without a trailing slash. Used by the Dispatch
> Web UI to authenticate a user via Proof Key Code Exchange \(PKCE\).

#### `DISPATCH_AUTHENTICATION_PROVIDER_PKCE_CLIENT_ID`

> The client id to send to the OpenID Connect endpoint.

#### `DISPATCH_AUTHENTICATION_PROVIDER_USE_ID_TOKEN` \['default': false\]

> Use `id_token` instead of default `access_token`. [Details](https://developer.okta.com/docs/reference/api/oidc/#tokens-and-claims)
> Depends on the identity provider.

#### Configuration for `dispatch-auth-provider-header`

> Authenticate users based on HTTP request headers. Useful when Dispatch is behind a reverse proxy performing authentication.

#### `DISPATCH_AUTHENTICATION_PROVIDER_HEADER_NAME` \['default': remote-user\]

{% hint style="warning" %}
Make sure the reverse proxy strips this header from incoming requests (i.e. user-provided). Failure to do so will result in authentication bypass.
{% endhint %}

> The HTTP request header to use as the user name, this value is case-insensitive.

### Persistence

#### `DATABASE_HOSTNAME`

> Dispatch relies on a `Postgres` database. This hostname should point to a supporter version of `Postgres (9.6+)`.

#### `DATABASE_CREDENTIALS` \[secret: True\]

> Credentials specified in `username:password` format to be used to authenticate to the `postgres` database.

#### `DATABASE_NAME` \[default: 'dispatch'\]

> Allows the user to specify the database name for the `Dispatch` backend.

#### `DATABASE_PORT` \[default: '5432'\]

> Allows the user to specify the database port for the `Dispatch` backend.

### Models

### Incident Cost

Dispatch [calculates](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/service.py#L279) the cost of an incident by adding up the time participants have spent on each incident role \(e.g., Incident Commander\) and applying an [engagement multiplier](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/service.py#L266) that's based on the incident role. It also includes time spent on incident review-related activities. Dispatch calculates and published the cost for all incidents [every 5 minutes](https://github.com/Netflix/dispatch/blob/develop/src/dispatch/incident/scheduled.py#L257).
