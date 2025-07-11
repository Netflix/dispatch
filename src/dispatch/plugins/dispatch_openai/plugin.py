"""
.. module: dispatch.plugins.openai.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""

import logging

from openai import OpenAI
from typing import TypeVar, Type

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_openai as openai_plugin
from dispatch.plugins.bases import ArtificialIntelligencePlugin
from dispatch.plugins.dispatch_openai.config import (
    OpenAIConfiguration,
)
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class OpenAIPlugin(ArtificialIntelligencePlugin):
    title = "OpenAI Plugin - Generative Artificial Intelligence"
    slug = "openai-artificial-intelligence"
    description = "Uses OpenAI's platform to allow users to ask questions in natural language."
    version = openai_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = OpenAIConfiguration

    def chat_completion(self, prompt: str) -> dict:
        client = OpenAI(api_key=self.api_key)

        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_message,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
        except Exception as e:
            logger.error(e)
            raise

        return completion.choices[0].message

    T = TypeVar("T", bound=BaseModel)

    def chat_parse(self, prompt: str, response_model: Type[T]) -> T:
        client = OpenAI(api_key=self.api_key)

        try:
            completion = client.chat.completions.parse(
                model=self.model,
                response_format=response_model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_message,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
        except Exception as e:
            logger.error(e)
            raise

        return completion.choices[0].message.parsed
