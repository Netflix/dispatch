from pydantic import BaseModel, Field
from pydantic.types import SecretStr


class OpsgenieConfiguration(BaseModel):
    """Opsgenie configuration description."""

    api_key: SecretStr = Field(title="API Key", description="")
    team_id: str = Field(title="Team ID", description="")
