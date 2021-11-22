from pydantic import Field, SecretStr

from dispatch.config import BaseConfigurationModel


class GoogleConfiguration(BaseConfigurationModel):
    """Google configuration"""

    developer_key: SecretStr = Field(
        title="Developer Key",
        description="This is used by the Google API Discovery Service and prevents rate limiting.",
    )
    service_account_client_email: str = Field(
        title="Service Account Client Email",
        description="The client_email value from your Google Cloud Platform (GCP) service account configuration file.",
    )
    service_account_client_id: str = Field(
        title="Service Account Client Id",
        description="The client_id value from your Google Cloud Platform (GCP) service account configuration file.",
    )
    service_account_private_key: SecretStr = Field(
        title="Service Account Private Key",
        description="The private_key value from your Google Cloud Platform (GCP) service account configuration file.",
    )
    service_account_private_key_id: str = Field(
        title="Service Account Private Key Id",
        description="The private_key_id value from your Google Cloud Platform (GCP) service account configuration file.",
    )
    service_account_delegated_account: str = Field(
        title="Service Account Delegated Account",
        description="Account to delegate to from the Google Cloud Platform (GCP) service account. Outgoing emails and other artifacts will appear to be from this account.",
    )
    service_account_project_id: str = Field(
        title="Service Account Project Id",
        description="The project_id value from your Google Cloud Platform (GCP) service account configuration file.",
    )
    google_domain: str = Field(
        title="Google Workspace Domain",
        description="Base domain for which this Google Cloud Platform (GCP) service account resides.",
    )
