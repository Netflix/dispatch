from pydantic import Field, HttpUrl, SecretStr

from dispatch.config import BaseConfigurationModel


class GithubConfiguration(BaseConfigurationModel):
    """Github configuration description."""

    pat: SecretStr = Field(
        title="Personal Access Token",
        description="Fine-grained personal access tokens.",
    )
    base_url: HttpUrl = Field(
        default="https://api.github.com",
        title="GitHub API Base URL",
        description="The base URL for the GitHub API. Use this to specify a GitHub Enterprise instance.",
    )
