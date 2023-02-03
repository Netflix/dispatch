from pydantic import Field, SecretStr, HttpUrl

from enum import Enum
from dispatch.config import BaseConfigurationModel


class HostingType(str, Enum):
    """Type of Confluence deployment."""

    cloud = "cloud"
    server = "server"


class ConfluenceConfigurationBase(BaseConfigurationModel):
    """Confluene configuration description."""

    api_url: HttpUrl = Field(
        title="API URL", description="This URL is used for communication with API."
    )
    hosting_type: HostingType = Field(
        "cloud", title="Hosting Type", description="Defines the type of deployment."
    )
    username: str = Field(
        title="Username", description="Username to use to authenticate to Confluence API."
    )
    password: SecretStr = Field(
        title="Password", description="Password to use to authenticate to Confluence API."
    )
