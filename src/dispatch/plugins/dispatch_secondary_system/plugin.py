"""
.. module: dispatch.plugins.secondary_system.plugin
    :platform: Unix
    :copyright: (c) 2024 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: David Whittaker <dwhittaker@netflix.com>
"""
import logging

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_secondary_system as secondary_system_plugin
from dispatch.plugins.bases import SecondarySystemPlugin
from dispatch.plugins.dispatch_secondary_system.config import (
    SecondarySytemConfiguration,
)

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

    def completion(self, prompt: str) -> dict:
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
