# Configuring GSuite

By default Dispatch ships with several GSuite plugins (Docs, Groups, Drive, etc.,). This page documents the available configuration for these plugins and the permissions required to enable them.

#### `GOOGLE_DOMAIN`

> Base domain for which this GCP service account resides.

#### `GOOGLE_DEVELOPER_KEY` [secret: True]

> This is used by the google discovery api and prevents rate limiting.

#### `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL`

> Client email for the GCP service account.

#### `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`

> Client ID for the GCP service account.

#### `GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT`

> Account to delegate to from the GCP service account.

#### `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY` [secret: True]

> Private key (PEM format) for the GCP service account.

#### `GOOGLE_ACCOUNT_PRIVATE_KEY_ID`

> Private key ID for the GCP service account.

#### `GOOGLE_ACCOUNT_PROJECT_ID`

> Project ID for the GCP service account.

#### `GOOGLE_USER_OVERRIDE` [default: None]

> Used for development to funnel all emails to a specific user.
