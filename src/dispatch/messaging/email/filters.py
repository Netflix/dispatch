import os
from datetime import datetime

import markdown
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from jinja2.ext import Extension
from markupsafe import Markup
from dispatch import config

here = os.path.dirname(os.path.realpath(__file__))


class SkipAllBlocksExtension(Extension):
    """Jinja2 extension that skips rendering and execution of all blocks."""

    def __init__(self, environment):
        super(SkipAllBlocksExtension, self).__init__(environment)
        environment.extend(skip_blocks=[])

    def filter_stream(self, stream):
        block_level = 0
        skip_level = 0
        in_endblock = False

        for token in stream:
            if token.type == "block_begin":
                block_level += 1
                skip_level = block_level

            if token.value == "endblock":
                in_endblock = True

            if skip_level == 0:
                yield token

            if token.type == "block_end":
                if in_endblock:
                    in_endblock = False
                    block_level -= 1

                    if skip_level == block_level + 1:
                        skip_level = 0


autoescape = bool(config.DISPATCH_ESCAPE_HTML)
env = SandboxedEnvironment(
    loader=FileSystemLoader(here), extensions=[SkipAllBlocksExtension], autoescape=autoescape
)


def format_datetime(value):
    return datetime.fromisoformat(value).strftime("%A, %B %d, %Y")


def format_markdown(value):
    return Markup(markdown.markdown(value))


env.filters["datetime"] = format_datetime
env.filters["markdown"] = format_markdown
