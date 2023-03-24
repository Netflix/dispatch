from pydantic import Field, SecretStr, HttpUrl
from typing import List, TypeVar

from dispatch.config import BaseConfigurationModel

Stop = TypeVar("Stop", str, List)


class OpenAIConfiguration(BaseConfigurationModel):
    """OpenAI configuration description."""

    api_url: HttpUrl = Field(
        "https://api.openai.com/v1/engines/text-davinci-002/completions",
        title="API URL",
        description="OpenAI's API URL.",
    )
    api_key: SecretStr = Field(title="API Key", description="Your secret OpenAI API key.")
    max_tokens: int = Field(
        50,
        title="Max Tokens",
        description="The maximum number of tokens to generate in the completion.",
    )
    temperature: float = Field(
        1, title="Temperature", description="What sampling temperature to use, between 0 and 2."
    )
    n: int = Field(
        1,
        title="Number of completions (n)",
        description="How many completions to generate for each prompt.",
    )
    stop: Stop = Field(
        None,
        title="Stop",
        description="Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.",
    )
