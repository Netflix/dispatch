from pydantic import Field, SecretStr

from dispatch.config import BaseConfigurationModel


class ZoomConfiguration(BaseConfigurationModel):
    """Zoom configuration description."""

    api_user_id: str = Field(title="Zoom API User Id")
    api_key: str = Field(title="API Key")
    api_secret: SecretStr = Field(title="API Secret")
    default_duration_minutes: int = Field(
        default=1440,  # 1 day
        title="Default Meeting Duration (Minutes)",
        description="Default duration in minutes for conference meetings. Defaults to 1440 minutes (1 day).",
    )
