from pydantic import Field

from dispatch.config import BaseConfigurationModel


class AWSConfiguration(BaseConfigurationModel):
    """AWS configuration description."""

    account_id: str = Field(title="AWS account id to use for signal enrichment.")
    region: str = Field(title="Region to use for enrichment")
