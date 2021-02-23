---
description: Staying up to date.
---

# Upgrading

If you're upgrading to a new major release, you should generate a new configuration file using the latest Dispatch version. Doing so ensures that any new settings are visible and configured if required.

Beyond that, upgrades are simple as bumping the version of Dispatch \(which will cause any changed dependencies to upgrade\), running data migrations, and restarting all related services.

{% hint style="info" %}
In some cases, you may want to stop services before doing the upgrade process or avoid intermittent errors.
{% endhint %}

## Upgrading Dispatch

### Upgrading the package

The easiest way to upgrade the Dispatch package using `pip`:

```bash
pip install --upgrade dispatch
```

You may prefer to install a fixed version rather than the latest, as it will allow you to control changes.

If you're installing from source code, you may have additional unfulfilled requirements, so take the necessary precautions of testing your environment before committing to the upgrade.

### Running Migrations

Just as during the initial setup, migrations are applied with the upgrade command.

```bash
dispatch database upgrade
```

### Restarting services

You'll need to ensure that _all_ of Dispatch's services are restarted after an upgrade. Restarting these services is required because Python loads modules in memory, and code changes will not be reflected until they are restarted.

These services include:

- server -- `dispatch server start`
- scheduler -- `dispatch scheduler start`
