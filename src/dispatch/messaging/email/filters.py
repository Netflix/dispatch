import os
from datetime import datetime

import markdown
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from markupsafe import Markup
from dispatch import config

here = os.path.dirname(os.path.realpath(__file__))


autoescape = bool(config.DISPATCH_ESCAPE_HTML)
env = SandboxedEnvironment(loader=FileSystemLoader(here), autoescape=autoescape)


def safe_format_datetime(value):
    print("safe format datetime", value)
    try:
        return datetime.fromisoformat(value).strftime("%A, %B %d, %Y")
    except (ValueError, TypeError):
        return ""


def safe_format_markdown(value):
    if not isinstance(value, str):
        return ""
    return Markup(markdown.markdown(value, output_format="html5", extensions=["extra"]))


env.filters["datetime"] = safe_format_datetime
env.filters["markdown"] = safe_format_markdown
