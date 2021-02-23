---
description: Configuration page for all Google Workspace plugins.
---

# Configuring Google Workspace Integration

The Google Workspace (Formerly GSuite) plugins allows the following features:

1. Create a incident specific folder
1. Create a group to manage permissions on that folder
1. Create a investigation document
1. Create google meet URLs
1. Send emails to participants

`DWD_ENABLED` config variable offers a choice to take the domain-wide delegation (DWD) route or not.

The DWD path requires that the domain-admin provide domain-wide control to the GCP service account that you create to use with dispatch for querying the API. This path allows the service account access to impersonate any domain user. Some Workspace APIs require domain-wide credentials while others don't.

The non-DWD path (where `DWD_ENABLED=False`) will use undelegated credentials generated from the GCP console and will only support 3 of the 5 supported Google Workspace APIs. Here the service account acts on behalf on itself and won't impersonate any domain-user.

{% hint style="info" %}
For the non-DWD path, you will need to use a shared-drive and add the service account email address to the shared drive as `Manager`. If we don't do this, the incident storage and documents will be created under the 15GB of drive space alloted to a service account which is limited and can run out quickly (or slowly based on the usage, but point is that it is limited amount of space).
{% endhint %}

| Workspace Component | DWD Requirement     |
|---------------------|---------------------|
| Groups API          | Doesn't require DWD |
| Drive API           | Doesn't require DWD |
| Docs API            | Doesn't require DWD |
| Gmail API           | Requires DWD        |
| Calendar API        | Requests DWD        |

{% hint style="info" %}
Dispatch ships with several Google Workspace plugins \(Docs, Groups, Drive, etc.,\). This page documents the available configuration for these plugins and the permissions required to enable them. These plugins are required for core functionality.
{% endhint %}

## Dispatch Configuration Variables

### `GOOGLE_DOMAIN` \[Required\]

> Base domain for which this Google Cloud Platform \(GCP\) service account resides.

### `GOOGLE_DEVELOPER_KEY` \[Required. Secret: True\]

> This is used by the Google API Discovery Service and prevents rate limiting.

### `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL` \[Required\]

> The `client_email` value from your Google Cloud Platform \(GCP\) service account configuration file.

### `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID` \[Required\]

> The `client_id` value from your Google Cloud Platform \(GCP\) service account configuration file.

### `GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT` \[Required\]

> Account to delegate to from the Google Cloud Platform \(GCP\) service account.
> Outgoing emails and other artifacts will appear to be from this account.

### `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY` \[Required. Secret: True\]

> The `private_key` value from your Google Cloud Platform \(GCP\) service account configuration file.

### `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID` \[Required\]

> The `private_key_id` value from your Google Cloud Platform \(GCP\) service account configuration file.

### `GOOGLE_SERVICE_ACCOUNT_PROJECT_ID` \[Required\]

> The `project_id` value from your Google Cloud Platform \(GCP\) service account configuration file.

### `GOOGLE_USER_OVERRIDE` \[Optional. Default: None\]

> Used for development to funnel all emails to a specific user.

### `DWD_ENABLED` \[Optional. Default: True\]

> This variable flags to dispatch that domain-wide delegation is enabled on the service account. This will be a boolean value.

### `GOOGLE_CUSTOMER_ID` \[Optional. Default: None\]

> Unique string assigned to each google workspace customer. It can be found by using these [instructions](https://support.google.com/a/answer/10070793?hl=en).

It is needed to use the [Groups API](https://cloud.google.com/identity/docs/how-to/create-google-groups#creating_a_google_group) which doesn't require admin SDK. It is passed as the parent resource under which groups are created, under which memberships are created.
NOTE: You've to add a 'C' as a prefix to the ID you get from the instructions above.

## Google Workspace Setup

To set up Goolge Workspace integration, you'll need to create some resources in Google Cloud Platform, and then link them to your Google Workspace organization.

## Enable Required APIs in Google Cloud Platform

Navigate to the Google Cloud Platform (GCP) [console](https://console.cloud.google.com/). You will want to
create a new GCP Project for Dispatch's integration.

Create a new service account within the GCP project (APIs & Services &gt; Credentials &gt; Create Credentials &gt; Service Account).
You do not need to assign any Google Cloud permissions to this service account when prompted.

Once created, download the JSON based key. You'll use these values to configure Dispatch:

* `project_id` -&gt; `GOOGLE_SERVICE_ACCOUNT_PROJECT_ID`
* `private_key_id` -&gt; `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID`
* `private_key` -&gt; `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY`
* `client_email` -&gt; `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL`
* `client_id` -&gt; `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`

Then, create a Developer API key \(APIs & Services &gt; Credentials &gt; Create Credentials &gt; API Key\), and set it to the value for `GOOGLE_DEVELOPER_KEY`.

Enable the following APIs \(APIs and Services &gt; Library\):

* Google Drive API
* Google Docs API
* Google Calendar API
* Gmail API
* Google Groups API (This API replaces Admin SDK for managing groups)

Finally, create your OAuth application which is how Google Workspace will authorize the service account and API key (APIs & Services &gt; OAuth Consent Screen).
Specify the following scopes:

```bash
# For non-DWD path
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/apps.groups.settings
https://www.googleapis.com/auth/cloud-identity.groups

# Add the below two scopes for the DWD path, in addition to the above scopes
https://www.googleapis.com/auth/admin.directory.group
https://mail.google.com/
https://www.googleapis.com/auth/calendar
```

**Note:** If you will not use Google Meet for your conference then you do not need the `https://www.googleapis.com/auth/calendar` scope.

## Connecting Dispatch to Google Workspace

Navigate to the Google Workspace Admin [Domain-wide Delegation](https://admin.google.com/ac/owl/domainwidedelegation) page
\(Security &gt; API Controls &gt; Domain-wide Delegation\) and add a new API client.

Enter the Client ID you used for `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`, and then paste in a comma-separated list of the OAuth scopes above.
