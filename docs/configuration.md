# Configuring Dispatch

This document describes additional configuration options available to the Dispatch server itself.

## First Install

During a new install, you will be prompted first for a walkthough of the Installation Wizard. This wilzard will help you get a few essential configuration options taken care of before begining.

Dispatch uses the same configuration system as [Starlette](https://www.starlette.io/config/).

By default, the config will be read from environment variables and/or `.env` files.

### General

DEBUG

LOG_LEVEL

SQLACHEMY_DATABASE_URI

SENTRY_DSN

JWKS_URL

### Incident Configuration

### Plugin Configuration

#### Slack

#### Google

#### Jira

#### Pagerduty
