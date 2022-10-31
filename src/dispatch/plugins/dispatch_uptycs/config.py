from pydantic import Field, SecretStr

from dispatch.config import BaseConfigurationModel


class UptycsConfiguration(BaseConfigurationModel):
    """Uptycs configuration description."""

    hostname: str = Field(
        title="Hostname", description="The host name for the Uptycs API.", default="ozark.uptycs.io"
    )
    customer_id: str = Field(
        title="Customer ID", description="Your customer id provided by Uptycs.", default=""
    )
    api_key: SecretStr = Field(
        title="API Key", description="This is the api key to the Uptycs API.", default=""
    )
    api_secret: SecretStr = Field(
        title="API Secret", description="This is the api secret to the Uptycs API.", default=""
    )
