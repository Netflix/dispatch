"""
.. module: dispatch.plugins.openai.plugin
	:platform: Unix
	:copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
	:license: Apache, see LICENSE for more details.
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""
import logging
import openai

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_openai as openai_plugin
from dispatch.plugins.bases import ArtificialIntelligencePlugin
from dispatch.plugins.dispatch_openai.config import (
    OpenAIConfiguration,
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

    def ask(self, prompt: str) -> str:
        openai.api_key = self.api_key

        try:
            response = openai.Completion.create(
                max_tokens=self.max_tokens,
                model=self.model,
                n=self.n,
                prompt=prompt,
                stop=self.stop,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.error(e)
            raise

        return response
