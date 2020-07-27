---
description: Configuration options for the Jira plugin.
---

# Configuring Jira

{% hint style="info" %}
Dispatch ships with Jira support. Each Jira installation is unique, so you will likely want to create a Jira specific plugin for your organization. This plugin is not required for core functionality, however a plugin of type `ticket` must always be enabled.
{% endhint %}

## `JIRA_BROWSER_URL` \[Required\]

> URL for Jira browser links.

## `JIRA_API_URL` \[Required\]

> URL for the Jira API server.

## `JIRA_USERNAME` \[Required\]

> Username for the Jira service account.

## `JIRA_PASSWORD` \[Required. Secret: True\]

> Password for the Jira service account.

## `JIRA_PROJECT_KEY` \[Required\]

> Key for Jira project.

## `JIRA_ISSUE_TYPE_ID` \[Required\]

> Id for Jira issue type.

