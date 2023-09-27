from pydantic import Field
from dispatch.config import BaseConfigurationModel


class AWSSQSConfiguration(BaseConfigurationModel):
    """SQS configuration description."""

    queue_name: str = Field(
        title="SQS Queue Name",
        description="SQS Queue Name, not the ARN.",
    )

    queue_owner: str = Field(
        title="SQS Queue Owner",
        description="SQS Queue Owner Account ID.",
    )

    region: str = Field(
        title="AWS Region",
        description="AWS Region.",
        default="us-east-1",
    )

    batch_size: int = Field(
        title="SQS Batch Size",
        description="SQS Batch Size.",
        default=10,
        le=10,
    )
