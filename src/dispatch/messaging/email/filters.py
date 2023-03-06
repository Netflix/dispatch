import os
from datetime import datetime

import markdown
from jinja2 import (
    Environment,
    FileSystemLoader,
)
from markupsafe import Markup
from dispatch import config

here = os.path.dirname(os.path.realpath(__file__))

autoescape = bool(config.DISPATCH_ESCAPE_HTML)
env = Environment(loader=FileSystemLoader(here), autoescape=autoescape)


def format_datetime(value):
    return datetime.fromisoformat(value).strftime("%A, %B %d, %Y")


def format_markdown(value):
    return Markup(markdown.markdown(value))


env.filters["datetime"] = format_datetime
env.filters["markdown"] = format_markdown
