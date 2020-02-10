# Configuring Dispatch

This document describes additional configuration options available to the Dispatch server itself.

## First Install

During a new install, you will be prompted first for a walkthough of the Installation Wizard. This wizard will help you get a few essential configuration options taken care of before begining.

Dispatch uses the same configuration system as [Starlette](https://www.starlette.io/config/).

By default, the config will be read from environment variables and/or `.env` files.

### General

#### `LOG_LEVEL` [optional][default: 'warning']

Controls the level of logging the application will perform during operations.

#### `STATIC_DIR` [optional][default: './src/static/dispatch/dist']

Controls where static content for the Dispatch UI should be served from. This can also be explicity set to `''` if you wish to serve static content outside of the Dispatch server.

#### `METRIC_PROVIDERS` [optional][default: ""]

A comma seperated list of metric providers Dispatch will send key system metrics to.

#### `SENTRY_DSN` [optional][default: none]

Optional configuration for using Sentry to report Dispatch errors.

#### `DISPATCH_HELP_EMAIL` [required]

Email address to be used by Dispatch when a help message is created.

#### `DISPATCH_HELP_SLACK_CHANNEL` [required]

Slack channel name to be used by Dispatch when a help message is created.

### Authentication

#### `JWKS_URL` [required]

Used by Dispatch's authentication backend to pull the JWKS public key from our specified provider. The result of this url is cached for up to 1 hour.

#### `VUE_APP_DISPATCH_OPEN_ID_CONNECT` [required]

Used by the Dispatch UI send the user via PKCE to a correct open id connect endpoint.

#### `VUE_APP_DISPATCH_CLIENT_ID` [required]

The client id to send to the open id connect endpoint.

### Persistence

#### `DATABASE_HOSTNAME` [required]

Dispatch relies on a `Postgres` database. This host name should point to a supporter version of `postgres`.

#### `DATABASE_CREDENTIALS` [required]

Credentials specified in `username:password` format to be used to authenticate to the `postgres` database.

#### `DATABASE_NAME` [optional][default: 'dispatch']

Allows the user to specify the database name for the `Dispatch` backend.

#### `DATABASE_PORT` [optional][default: '5432']

Allows the user to specify the database port fo the `Dispatch` backend.

### Models

### Incident Cost

#### `ANNUAL_COST_EMPLOYEE` [optional][default: '650000]

Used for incident cost modeling, specifices the total `all-in` cost for a average employee working on incidents.
