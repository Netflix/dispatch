---
description: Configuration page for all G Suite plugins.
---

# Configuring G Suite

{% hint style="info" %}
Dispatch ships with several G Suite plugins \(Docs, Groups, Drive, etc.,\). This page documents the available configuration for these plugins and the permissions required to enable them. These plugins are required for core functionality.
{% endhint %}

### `GOOGLE_DOMAIN` \[Required\]

> Base domain for which this Google Cloud Platform \(GCP\) service account resides.

### `GOOGLE_DEVELOPER_KEY` \[Required. Secret: True\]

> This is used by the Google API Discovery Service and prevents rate limiting.

### `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL` \[Required\]

> Client email for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID` \[Required\]

> Client ID for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT` \[Required\]

> Account to delegate to from the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY` \[Required. Secret: True\]

> Private key \(PEM format\) for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID` \[Required\]

> Private key ID for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_PROJECT_ID` \[Required\]

> Project ID for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_USER_OVERRIDE` \[Optional. Default: None\]

> Used for development to funnel all emails to a specific user.

## Enable Required APIs

This is meant to provide guidance on enabling Dispatch's G Suite plugins, your organization may differ slightly.

Navigate to the Google Cloud Platform \(GCP\) [console](https://console.cloud.google.com/).

Create a new service account \(APIs & Services &gt; Credentials &gt; Create Credentials &gt; Service Account\).

Once created, download the JSON based key and use it's values to populate the above configuration values:

* `project_id` -&gt; `GOOGLE_SERVICE_ACCOUNT_PROJECT_ID`
* `private_key_id` -&gt; `GOOGLE_SERVICE_PRIVATE_KEY_ID`
* `private_key` -&gt; `GOOGLE_SERVICE_PRIVATE_KEY`
* `client_email` -&gt; `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL`
* `client_id` -&gt; `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`

Create a Developer API key \(APIs & Services &gt; Credentials &gt; Create Credentials &gt; API Key\), and set the value of `GOOGLE_DEVELOPER_KEY`.

Enable the following APIs \(APIs and Services &gt; Library\):

* Google Drive API
* Google Docs API
* Google Calendar API
* Gmail API
* Admin SDK \(necessary to create and manage groups\)

{% hint style="info" %}
If you are planning on using Google Drive storage you must enable the folder sharing beta.

[https://support.google.com/a/answer/9890318?hl=en\#:~:text=Help%20CenterCommunity-,Folder%20sharing%20in%20shared%20drives%20\(beta\),folders%20within%20a%20shared%20drive](https://support.google.com/a/answer/9890318?hl=en#:~:text=Help%20CenterCommunity-,Folder%20sharing%20in%20shared%20drives%20%28beta%29,folders%20within%20a%20shared%20drive)

To signup:  
[https://docs.google.com/forms/d/e/1FAIpQLSfrILe0\_bPkkI7pxfr-4rHk0qcajrUOHTcmrWPOVLo0SKNF7A/viewform](https://docs.google.com/forms/d/e/1FAIpQLSfrILe0_bPkkI7pxfr-4rHk0qcajrUOHTcmrWPOVLo0SKNF7A/viewform)
{% endhint %}

Finally, map the `client_id` of the created service with the required OAuth2 scopes.

Navigate to admin [home](https://admin.google.com/AdminHome?chromeless=1#OGX:ManageOauthClients%20) \(Security &gt; Advanced Settings &gt; Manage API Client Access\), and add the following scopes:

```text
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/drive
https://mail.google.com/
https://www.googleapis.com/auth/admin.directory.group
https://www.googleapis.com/auth/apps.groups.settings
https://www.googleapis.com/auth/calendar
```

**Note:** If you will not use Google Meet for your conference then you do not need the `https://www.googleapis.com/auth/calendar` scope.

Then construct this link and click it:

```text
https://admin.google.com/AdminHome?clientScopeToAdd=https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/drive,https://mail.google.com/,https://www.googleapis.com/auth/admin.directory.group,https://www.googleapis.com/auth/apps.groups.settings,https://www.googleapis.com/auth/calendar
&clientNameToAdd=<INSERTCLIENTIDHERE>&chromeless=1#OGX:ManageOauthClients
```

