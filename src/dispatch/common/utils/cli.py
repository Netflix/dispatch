import os
import sys
import traceback
import logging
import pkg_resources
from sqlalchemy.exc import SQLAlchemyError

import click
from dispatch.plugins.base import plugins, register

from .dynamic_click import params_factory


logger = logging.getLogger(__name__)


def chunk(l, n):
    """Chunk a list to sublists."""
    for i in range(0, len(l), n):
        yield l[i : i + n]


# Plugin endpoints should determine authentication # TODO allow them to specify (kglisson)
def install_plugin_events(api):
    """Adds plugin endpoints to the event router."""
    for plugin in plugins.all():
        if plugin.events:
            api.include_router(plugin.events, prefix="/events", tags=["events"])


def install_plugins():
    """
    Installs plugins associated with dispatch
    :return:
    """

    for ep in pkg_resources.iter_entry_points("dispatch.plugins"):
        logger.debug(f"Attempting to load plugin: {ep.name}")
        try:
            plugin = ep.load()
            register(plugin)
            logger.debug(f"Successfully loaded plugin: {ep.name}")
        except KeyError as e:
            logger.warning(f"Failed to load plugin: {ep.name} Reason: {e}")
        except SQLAlchemyError:
            logger.error(
                "Something went wrong with creating plugin rows, is the database setup correctly?"
            )
        except Exception:
            logger.error(f"Failed to load plugin {ep.name}:{traceback.format_exc()}")
        else:
            if not plugin.enabled:
                continue


def with_plugins(plugin_type: str):

    """
    A decorator to register external CLI commands to an instance of
    `click.Group()`.
    Parameters
    ----------
    plugin_type : str
    Plugin type to create subcommands for.
    Returns
    -------
    click.Group()
    """

    def decorator(group):
        if not isinstance(group, click.Group):
            raise TypeError("Plugins can only be attached to an instance of click.Group()")

        for p in plugins.all(plugin_type=plugin_type) or ():
            # create a new subgroup for each plugin
            name = p.slug.split("-")[0]
            plugin_group = click.Group(name)
            try:
                for command in p.commands:
                    command_func = getattr(p, command)
                    props = get_plugin_properties(p.schema)
                    params = params_factory([props])
                    command_obj = click.Command(
                        command, params=params, callback=command_func, help=command_func.__doc__
                    )
                    plugin_group.add_command(command_obj)
            except Exception:
                # Catch this so a busted plugin doesn't take down the CLI.
                # Handled by registering a dummy command that does nothing
                # other than explain the error.
                plugin_group.add_command(BrokenCommand(p.slug, plugin_type))

            group.add_command(plugin_group)
        return group

    return decorator


class BrokenCommand(click.Command):

    """
    Rather than completely crash the CLI when a broken plugin is loaded, this
    class provides a modified help message informing the user that the plugin is
    broken and they should contact the owner.  If the user executes the plugin
    or specifies `--help` a traceback is reported showing the exception the
    plugin loader encountered.
    """

    def __init__(self, name, plugin_type):

        """
        Define the special help messages after instantiating a `click.Command()`.
        """

        click.Command.__init__(self, name)

        util_name = os.path.basename(sys.argv and sys.argv[0] or __file__)

        if os.environ.get("CLICK_PLUGINS_HONESTLY"):  # pragma no cover
            icon = "\U0001F4A9"
        else:
            icon = "\u2020"

        self.help = (
            f"\nWarning: plugin could not be loaded. Contact "
            f"its author for help.\n\n\b\n {traceback.format_exc()}"
        )
        self.short_help = f"{icon} Warning: could not load plugin. See `{util_name} {plugin_type} {self.name} --help`."

    def invoke(self, ctx):

        """
        Print the traceback instead of doing nothing.
        """

        click.echo(self.help, color=ctx.color)
        ctx.exit(1)

    def parse_args(self, ctx, args):
        return args


def get_plugin_properties(json_schema):
    for _, v in json_schema["definitions"].items():
        return v["properties"]


def add_plugins_args(f):
    """Adds installed plugin options."""
    schemas = []
    if isinstance(f, click.Command):
        for p in plugins.all():
            schemas.append(get_plugin_properties(p.schema))
        f.params.extend(params_factory(schemas))
    else:
        if not hasattr(f, "__click_params__"):
            f.__click_params__ = []

        for p in plugins.all():
            schemas.append(get_plugin_properties(p.schema))
        f.__click_params__.extend(params_factory(schemas))

    return f
