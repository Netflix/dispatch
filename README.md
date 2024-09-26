# About

## What's Dispatch?

Put simply, Dispatch is:

> All of the ad-hoc things you’re doing to manage incidents today, done for you, and a bunch of other things you should've been doing, but have not had the time!

Dispatch helps us effectively manage security incidents by deeply integrating with existing tools used throughout an organization \(Slack, GSuite, Jira, etc.,\) Dispatch is able to leverage the existing familiarity of these tools to provide orchestration instead of introducing another tool.

This means you can let Dispatch focus on creating resources, assembling participants, sending out notifications, tracking tasks, and assisting with post-incident reviews; allowing you to focus on actually fixing the issue!
![thumb-1](https://github.com/Netflix/dispatch/raw/master/docs/images/screenshots/thumb-1.png) ![thumb-2](https://github.com/Netflix/dispatch/raw/master/docs/images/screenshots/thumb-2.png) ![thumb-3](https://github.com/Netflix/dispatch/raw/master/docs/images/screenshots/thumb-3.png) ![thumb-4](https://github.com/Netflix/dispatch/raw/master/docs/images/screenshots/thumb-4.png)

## Development

This repo requires the use of a python virtual environment. To create a virtual environment, run the following command:

```bash
python -m venv ./py_venv
source py_venv/bin/activate
```

after that, you can install dependencies with

```bash
python3 -m pip install -r requirements-dev.in
python3 -m pip install -r requirements-base.in
```

## Project resources

- [Source Code](https://github.com/veho-technologies/dispatch)
- [Docs](https://netflix.github.io/dispatch/)
- [Docker](https://github.com/Netflix/dispatch-docker)
