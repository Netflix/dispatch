from pydantic import Field, SecretStr
from typing import List, TypeVar

from dispatch.config import BaseConfigurationModel

Stop = TypeVar("Stop", str, List)


class OpenAIConfiguration(BaseConfigurationModel):
    """OpenAI configuration description."""

    api_key: SecretStr = Field(title="API Key", description="Your secret OpenAI API key.")
    model: str = Field("text-davinci-003", title="Model", description="")
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
