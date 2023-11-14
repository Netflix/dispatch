from pydantic import Field, SecretStr

from dispatch.config import BaseConfigurationModel


class OpenAIConfiguration(BaseConfigurationModel):
    """OpenAI configuration description."""

    api_key: SecretStr = Field(title="API Key", description="Your secret OpenAI API key.")
    model: str = Field(
        "gpt-3.5-turbo",
        title="Model",
        description="Available models can be found at https://platform.openai.com/docs/models",
    )
    system_message: str = Field(
        "You are a helpful assistant.",
        title="System Message",
        description="The system message to help set the behavior of the assistant.",
    )
