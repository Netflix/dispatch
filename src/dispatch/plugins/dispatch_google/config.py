from pydantic.main import BaseModel, Field


class GoogleConfiguration(BaseModel):
    """Google configuration description."""

    developer_key: str = Field(title="Developer Key", description="")
    service_account_client_email: str = Field(title="Service Account Client Email", description="")
    service_account_client_id: str = Field(title="Service Account Client Id", description="")
    service_account_private_key: str = Field(title="Service Account Private Key", description="")
    service_account_private_key_id: str = Field(
        title="Service Account Private Key Id", description=""
    )
    service_account_delegated_account: str = Field(
        title="Service Account Delegated Account", description=""
    )
    service_account_project_id: str = Field(title="Service Account Project Id", description="")
    google_domain: str = Field("Google Workspace Domain", description="")

    class Config:
        title = "Google Configuration"
