"""
.. module: dispatch.plugins.openai.plugin
	:platform: Unix
	:copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
	:license: Apache, see LICENSE for more details.
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""
import json
import logging
import requests

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

    def _generate_headers(self):
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

    def ask(self, prompt):
        payload = {
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "n": self.n,
            "stop": self.stop,
            "temperature": self.temperature,
        }
        headers = self._generate_headers()
        response = requests.post(self.base_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            return response.json()["choices"]
        else:
            error_message = f"Error {response.status_code}: {response.text}"
            logger.error(error_message)
            raise Exception(error_message)
