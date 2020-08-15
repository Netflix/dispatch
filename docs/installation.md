# Installation

Dispatch relies on multiple services to work, which are all orchestrated by `Docker Compose`.

### Requirements

* [Docker](https://www.docker.com/) 17.05.0+
* [Docker Compose](https://docs.docker.com/compose/) 1.19.0+
* A dedicated \(sub\)domain to host Dispatch on \(for example, dispatch.yourcompany.com\).
* At least 2400MB memory
* 2 CPU Cores

## Installing Dispatch Server

We strongly recommend using Docker, for installing Dispatch and all its services. If you need to do something custom, you can use this repository as the basis of your setup. If you do not wish to use the Docker images we provide, you can still find Dispatch on PyPI; however, we don't recommend that method. You'll need to work your way back from the main Dispatch image. It is not too hard, but you are likely to spend a lot more time and hit some bumps.

To install Dispatch from the repository, clone the repository locally:

```bash
git clone https://github.com/Netflix/dispatch-docker.git
```

Before starting the installation, we strongly recommend you check out [how to configure your Dispatch instance](configuration/) as you'd need to rebuild your images \(`docker-compose build`\) if you want to change your configuration settings. You may copy and edit the example configs provided in the repository. If none exists, the install script will use these examples as actual configurations.

{% hint style="info" %}
Note: Dispatch will not start without at least a few required configuration variables, see the example [env](https://github.com/Netflix/dispatch/blob/develop/docker/.env.example).
{% endhint %}

{% hint style="info" %}
Note: Dispatch does not contain any data by default. For evaluation purposes, we do provide an example data set located [here](https://github.com/Netflix/dispatch/blob/develop/data/dispatch-sample-data.dump). For instructions for restoring this data see [here](https://hawkins.gitbook.io/dispatch/cli#restore-dump).
{% endhint %}

To start, run the install script:

```bash
./install.sh
```

