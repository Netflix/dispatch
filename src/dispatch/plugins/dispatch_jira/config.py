from pydantic.main import BaseModel, Field, SecretStr, HttpUrl
from enum import Enum


class HostingType(str, Enum):
    cloud = "cloud"
    server = "server"


class JiraConfiguration(BaseModel):
    """Jira configuration description."""

    api_url: HttpUrl = Field(title="API URL", description="")
    browser_url: HttpUrl = Field(title="Browser URL", description="")
    hosting_type: HostingType = Field(title="Hosting Type", description="")
    issue_type_name: str = Field(title="Issue Type Name", description="")
    username: str = Field(title="Username", description="")
    password: SecretStr = Field(title="Password", description="")
    project_id: str = Field(title="Project Id", description="")
