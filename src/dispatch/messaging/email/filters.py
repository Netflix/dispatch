import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

here = os.path.dirname(os.path.realpath(__file__))
env = Environment(loader=FileSystemLoader(here), autoescape=True)


def format_datetime(value):
    return datetime.fromisoformat(value).strftime("%A, %B %d, %Y")


env.filters["datetime"] = format_datetime
