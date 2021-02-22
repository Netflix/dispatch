---
description: Quick guide for setting your environment for Dispatch development.
---

# Environment

{% hint style="info" %}
This guide assumes you're using an OS of the Linux/Unix variant \(Ubuntu/OS X\) and is not meant to be exhaustive.
{% endhint %}

## Easy Mode

Install Dispatch with PIP:

```bash
> DISPATCH_LIGHT_BUILD=1 pip install -e .[dev]
```

Run dev server:

```bash
> STATIC_DIR="" dispatch server develop # or set STATIC_DIR to "" in .env
```

This command will run the webpack-dev-server in another process when starting the dev server and forward static files through HTTP.

## API

### System

Ensure you have python3 available on your system:

```bash
> which python3
/home/kglisson/.pyenv/shims/python3
```

Above, you can see that we're using [pyenv](https://github.com/pyenv/pyenv) to manage our python versions on our system. The rest of the guide will assume pyenv is being used.

Once we have python installed, let's ensure it's a new enough version:

```bash
> python --version
Python 3.7.3
```

{% hint style="info" %}
Dispatch uses async functionality and requires `python 3.7.3+`.
{% endhint %}

Create a new virtualenv just for Dispatch:

```bash
> pyenv virtualenv dispatch
```

Install Dispatch with pip:

```bash
> pip install -e /path/to/dispatch
```

Test it by seeing if the `dispatch` command is in your path:

```bash
> dispatch --help
```

## UI

Dispatch uses the [Vue Cli](https://cli.vuejs.org/) to manage its single-page app \(SPA\) and the [Vuetify](https://vuetifyjs.com/en/) framework for material based components.

To get started developing with Vue, first navigate to the root static directory:

```bash
> cd <dispatch-source-patch>/src/dispatch/static/dispatch
```

Ensure you have node installed:

```bash
> which node
/home/kglisson/.nvm/versions/node/v12.7.0/bin/node
```

Notice that we are using [nvm](https://github.com/nvm-sh/nvm) to manage our installations of Node. The rest of the guide assumes the usage of nvm.

Check to make sure we have the correct version of Node:

```bash
> node --version
v12.7.0
```

{% hint style="info" %}
To correctly build it's components Dispatch requires node 12.7.0+
{% endhint %}

Install required node modules with `npm` :

```bash
> npm install
```

Test the development server:

```bash
> npm run serve
```
