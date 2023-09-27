from pydantic import Field
from dispatch.config import BaseConfigurationModel


class AWSSQSConfiguration(BaseConfigurationModel):
    """Signal SQS configuration"""

    queue_name: str = Field(
        title="Queue Name",
        description="Queue Name, not the ARN.",
    )

    queue_owner: str = Field(
        title="Queue Owner",
        description="Queue Owner Account ID.",
    )

    region: str = Field(
        title="AWS Region",
        description="AWS Region.",
        default="us-east-1",
    )

    batch_size: int = Field(
        title="Batch Size",
        description="Number of messages to retrieve from SQS.",
        default=10,
        le=10,
    )
