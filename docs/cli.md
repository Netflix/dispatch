---
description: Overview of the Dispatch CLI.
---

# CLI

Dispatch ships with a robust CLI, providing configuration, server, scheduler, plugin, database and shell commands. Here we'll give a partial overview; if you'd like a complete list of Dispatch commands available via the CLI, please use the command `dispatch --help` once you have installed the application.

## Server

The server sub-command contains all Dispatch server related commands.

```bash
> dispatch server --help                                                                        develop ⬇ ◼
Usage: dispatch server [OPTIONS] COMMAND [ARGS]...

  Container for all dispatch server commands.

Options:
  --help  Show this message and exit.

Commands:
  config   Prints the current config as dispatch sees it.
  develop  Runs a simple server for development.
  routes   Prints all available routes.
  shell    Starts an ipython shell importing our app.
  start
```

### Config

The `config` command is helpful in debugging as it shows the configuration variables as they are seen by the server \(combining envvars, defaults and the .env file\).

```bash
> dispatch server config
> 
Key                                       Value
----------------------------------------  -----------------------
DISPATCH_DOMAIN                           example.com
STATIC_DIR
METRIC_PROVIDERS                          spectator-metric
...
```

### Develop

The `develop` command is used to start a development server. This server will continually watch for file changes and reload the server accordingly. You'll find it useful to combine this with a `DEBUG` log level, as below.

```bash
> dispatch server develop --log-level debug
```

### Routes

The `routes` command is useful for development. It shows a not only which endpoints at which the server is currently listening, but also the HTTP verb methods that are accepted, and whether or not authentication is enabled for the endpoint.

```bash
> dispatch server routes
Path                                  Authenticated    Methods
------------------------------------  ---------------  ---------
/healthcheck                          False            GET
/documents/                           True             GET
/documents/{document_id}              True             GET
/documents/                           True             POST
...
```

### Shell

The `shell` command is useful for development. It drops you into a python interactive shell with the same context as the server itself.

```bash
> dispatch server shell
```

### Start

The `start` command is used to start a production grade Dispatch web server. It's really an alias to the [uvicorn](https://www.uvicorn.org/) webserver, so it contains all of the options and flags available with that server.

```bash
> dispatch server start --help
Usage: dispatch server start [OPTIONS] APP

Options:
  --host TEXT                     Bind socket to this host.  [default:
                                  127.0.0.1]
  --port INTEGER                  Bind socket to this port.  [default: 8000]
  --uds TEXT                      Bind to a UNIX domain socket.
  --fd INTEGER                    Bind to socket from this file descriptor.
  --reload                        Enable auto-reload.
  --reload-dir TEXT               Set reload directories explicitly, instead
                                  of using the current working directory.
  ...
```

To start Dispatch you will need to tell the start command where to find the `dispatch` [ASGI](https://asgi.readthedocs.io/en/latest/) application. For example a common set of flags might be:

```bash
> dispatch server start dispatch.main:app --workers 6 --host 127.0.0.1 --port 8000 --proxy-headers
```

## Scheduler

The `scheduler` command contains all of the Dispatch scheduler logic.

```bash
> dispatch scheduler --help
Usage: dispatch scheduler [OPTIONS] COMMAND [ARGS]...

  Container for all dispatch scheduler commands.

Options:
  --help  Show this message and exit.

Commands:
  list   Prints and runs all currently configured periodic tasks, in...
  start  Starts the scheduler.
```

### List

The `list` command lists all tasks that are currently registered with the scheduler. Today the scheduler periods are hard coded and cannot be adjusted.

```bash
> dispatch scheduler list
Task Name                        Period          At Time
-------------------------------  --------------  ---------
incident-status-report-reminder  1:00:00
incident-daily-summary           1 day, 0:00:00  18:00:00
calculate-incident-cost          0:05:00
incident-task-reminders          1:00:00
incident-task-sync               0:00:30
term-sync                        1:00:00
document-term-sync               1 day, 0:00:00
application-sync                 1:00:00
```

### Start

The `start` command starts the scheduler, and allows tasks be executed based on the defined period.

```bash
> dispatch scheduler start
Starting scheduler...
```

Often it's helpful to run a particular task immediately:

```bash
> dispatch scheduler start incident-status-report-reminder --eager
```

## Database

The `database` command contains all of the Dispatch database logic.

```bash
> dispatch database --help
Usage: dispatch database [OPTIONS] COMMAND [ARGS]...

  Container for all dispatch database commands.

Options:
  --help  Show this message and exit.

Commands:
  downgrade      Downgrades database schema to next newest version.
  drop           Drops all data in database.
  heads          Shows the heads of the database.
  history        Shows the history of the database.
  init           Initializes a new database.
  populate       Populates database with default values.
  revision       Create new database revision.
  sync-triggers  Ensures that all database triggers have been installed.
  upgrade        Upgrades database schema to newest version.
```

{% hint style="info" %}
Note: The database command is a combination of custom commands and `alembic` commands. For more information about alembic database migrations see [here](https://alembic.sqlalchemy.org/en/latest/).
{% endhint %}

### Init

The `init` command takes a fresh database and creates the necessary tables and values for Dispatch to operate.

```bash
> dispatch database init
```

### Revision

The `revision` command is an `alembic` command that creates a new database schema revision based on the models defined within the application.

It's most often used with the `--autogenerate` flag:

```bash
> dispatch database revision --autogenerate
```

### Upgrade/Downgrade

The `upgrade` and `downgrade` commands manage how `alembic` database migrations are deployed, allowing you to move the database forward and backward through revisions. You'll often need to run the `upgrade` command after installing a new version of Dispatch.

```bash
> dispatch database upgrade
```

### Restore/Dump

The `restore` and `dump` commands allow you to quickly backup and restore the Dispatch database. They can also be used to load our [example](https://github.com/Netflix/dispatch/blob/develop/data/dispatch-sample-data.dump) data set into your Dispatch installation.

Today, the `.dump` file must be located in `$CWD` and must be named `dispatch-backup.dump`

## Plugins

The `plugin` command contains all of the logic for dealing with Dispatch's plugins.

### List

The `list` command lists all currently available plugins. This is useful in determining which plugins are available to be used via configuration variables.

```bash
> dispatch database list
Title                             Slug                            Version     Type               Author         Description
--------------------------------  ------------------------------  ----------  -----------------  -------------  ---------------------------------------------------------
Dispatch - Document Resolver      dispatch-document-resolver      0.1.0       document-resolver  Kevin Glisson  Uses dispatch itself to resolve incident documents.
Dispatch - Participants           dispatch-participants           0.1.0       participant        Kevin Glisson  Uses dispatch itself to determine participants.
Google Docs - Document            google-docs-document            0.1.0       document           Kevin Glisson  Uses google docs to manage document contents.
Google Gmail - Conversation       google-gmail-conversation       0.1.0       conversation       Kevin Glisson  Uses gmail to facilitate conversations.
Google Group - Participant Group  google-group-participant-group  0.1.0       participant_group  Kevin Glisson  Uses Google Groups to help manage participant membership.
...
```

