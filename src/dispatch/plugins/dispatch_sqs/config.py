from pydantic import Field

from dispatch.config import BaseConfigurationModel


class SQSConfiguration(BaseConfigurationModel):
    """SQS configuration description."""

    arn: str = Field(title="SQS ARN to use for signal ingestion.")
