---
description: Configuration page for all G Suite plugins.
---

# Configuring G Suite Integration

{% hint style="info" %}
Dispatch ships with several G Suite plugins \(Docs, Groups, Drive, etc.,\). This page documents the available configuration
for these plugins and the permissions required to enable them. These plugins are required for core functionality.
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

## G Suite Setup

To set up G Suite integration, you'll need to create some resources in Google Cloud Platform, and then link them to your
G Suite organization.

## Enable Required APIs in Google Cloud Platform

Navigate to the Google Cloud Platform \(GCP\) [console](https://console.cloud.google.com/). You will want to
create a new GCP Project for Dispatch's integration.

Create a new service account within the GCP project \(APIs & Services &gt; Credentials &gt; Create Credentials &gt; Service Account\). 
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
* Admin SDK \(necessary to create and manage groups\)

Finally, create your OAuth application which is how G Suite will authorize the service account and API key \(APIs & Services &gt; OAuth Consent Screen\).
Specify the following scopes:

```text
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/drive
https://mail.google.com/
https://www.googleapis.com/auth/admin.directory.group
https://www.googleapis.com/auth/apps.groups.settings
https://www.googleapis.com/auth/calendar
```

**Note:** If you will not use Google Meet for your conference then you do not need the `https://www.googleapis.com/auth/calendar` scope.

## Connecting Dispatch to G Suite

Navigate to the G Suite Admin [Domain-wide Delegation](https://admin.google.com/ac/owl/domainwidedelegation) page 
\(Security &gt; API Controls &gt; Domain-wide Delegation\) and add a new API client. 

Enter the Client ID you used for `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`, and then paste in a comma-separated list of the OAuth scopes above.
