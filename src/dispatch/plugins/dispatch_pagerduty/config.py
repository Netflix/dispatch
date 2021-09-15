from pydantic import BaseModel, Field, SecretStr, EmailStr


class PagerdutyConfiguration(BaseModel):
    """Pagerduty configuration description."""

    api_key: SecretStr = Field(title="API Key", description="")
    from_email: EmailStr = Field(title="API from Email", description="")
