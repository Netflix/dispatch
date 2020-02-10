import json
from functools import partial
from typing import List

import click


from .json_schema import COMPLEX_TYPES, json_schema_to_click_type, handle_oneof


CORE_COMMANDS = {
    "required": "'{}' required schema",
    "schema": "'{}' full schema",
    "metadata": "'{}' metadata",
    "defaults": "'{}' default values",
}


# TODO figure out how to validate across opts
def validate_schema_callback(ctx, param, value):
    """Ensures options passed fulfill what plugins are expecting."""
    return value


def params_factory(schemas: List[dict]) -> list:
    """
    Generates list of :class:`click.Option` based on a JSON schema

    :param schemas:  JSON schemas to operate on
    :return: Lists of created :class:`click.Option` object to be added to a :class:`click.Command`
    """
    params = []
    unique_decls = []
    for schema in schemas:
        for prpty, prpty_schema in schema.items():
            multiple = False
            choices = None

            if any(char in prpty for char in ["@"]):
                continue

            if prpty_schema.get("type") in COMPLEX_TYPES:
                continue

            if prpty_schema.get("duplicate"):
                continue

            elif not prpty_schema.get("oneOf"):
                click_type, description, choices = json_schema_to_click_type(prpty_schema)
            else:
                click_type, multiple, description = handle_oneof(prpty_schema["oneOf"])
                # Not all oneOf schema can be handled by click
                if not click_type:
                    continue

            # Convert bool values into flags
            if click_type == click.BOOL:
                param_decls = [get_flag_param_decals_from_bool(prpty)]
                click_type = None
            else:
                param_decls = [get_param_decals_from_name(prpty)]

            if description:
                description = description.capitalize() + "."
                default = prpty_schema.get("default")

                if default:
                    description += f" [Default: {default}]"

                if multiple:
                    if not description.endswith("."):
                        description += "."
                    description += " Multiple usages of this option are allowed"

            param_decls = [x for x in param_decls if x not in unique_decls]
            if not param_decls:
                continue

            unique_decls += param_decls
            option = partial(
                click.Option,
                param_decls=param_decls,
                help=description,
                default=prpty_schema.get("default"),
                callback=validate_schema_callback,
                multiple=multiple,
            )

            if choices:
                option = option(type=choices)
            elif click_type:
                option = option(type=click_type)
            else:
                option = option()

            params.append(option)
    return params


def func_factory(p, method: str) -> callable:
    """
    Dynamically generates callback commands to correlate to provider public methods
    """

    def callback(pretty: bool = False):
        res = getattr(p, method)
        dump = partial(json.dumps, indent=4) if pretty else partial(json.dumps)
        click.echo(dump(res))

    return callback


def get_param_decals_from_name(option_name: str) -> str:
    """Converts a name to a param name"""
    name = option_name.replace("_", "-")
    return f"--{name}"


def get_flag_param_decals_from_bool(option_name: str) -> str:
    """Return a '--do/not-do' style flag param"""
    name = option_name.replace("_", "-")
    return f"--{name}/--no-{name}"
