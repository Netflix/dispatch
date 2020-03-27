# Configuring G Suite

By default Dispatch ships with several G Suite plugins \(Docs, Groups, Drive, etc.,\). This page documents the available configuration for these plugins and the permissions required to enable them.

### `GOOGLE_DOMAIN`

> Base domain for which this Google Cloud Platform \(GCP\) service account resides.

### `GOOGLE_DEVELOPER_KEY` \[secret: True\]

> This is used by the Google API Discovery Service and prevents rate limiting.

### `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL`

> Client email for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`

> Client ID for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT`

> Account to delegate to from the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY` \[secret: True\]

> Private key \(PEM format\) for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_ACCOUNT_PRIVATE_KEY_ID`

> Private key ID for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_ACCOUNT_PROJECT_ID`

> Project ID for the Google Cloud Platform \(GCP\) service account.

### `GOOGLE_USER_OVERRIDE` \[default: None\]

> Used for development to funnel all emails to a specific user.

## Enable Required APIs

This is meant to provide guidance on enabling Dispatch's G Suite plugins, your organization may differ slightly.

Navigate to the Google Cloud Platform \(GCP\) [console](https://console.cloud.google.com/).

Create a new service account \(APIs & Services &gt; Credentials &gt; Create Credentials &gt; Service Account\).

Once created, download the JSON based key and use it's values to populate the above configuration values:

* `project_id` -&gt; `GOOGLE_ACCOUNT_PROJECT_ID`
* `private_key_id` -&gt; `GOOGLE_SERVICE_PRIVATE_KEY_ID`
* `private_key` -&gt; `GOOGLE_SERVICE_PRIVATE_KEY`
* `client_email` -&gt; `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL`
* `client_id` -&gt; `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`

Create a Developer API key \(APIs & Services &gt; Credentials &gt; Create Credentials &gt; API Key\), and set the value of `GOOGLE_DEVELOPER_KEY`.

Enable the following APIs \(APIs and Services &gt; Library\):

* Google Drive API
* Google Docs API
* Gmail API
* Admin SDK

Finally, map the `client_id` of the created service with the required OAuth2 scopes.

Navigate to admin [home](https://admin.google.com/AdminHome?chromeless=1#OGX:ManageOauthClients%20) \(Security &gt; Advanced Settings &gt; Manage API Client Access\), and add the following scopes:

```text
https://www.googleapis.com/auth/document
https://www.googleapis.com/auth/drive
https://mail.google.com/
https://www.googleapis.com/auth/admin.directory.group
https://www.googleapis.com/auth/apps.groups.settings
```

