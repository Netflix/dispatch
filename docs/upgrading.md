# Upgrading

If you're upgrading to a new major release, it's always recommended to start by generating a new configuration file \(using the new version of Dispatch\). This will ensure that any new settings which may have been added are clearly visable and get configurated correctly.

Beyond that, upgrades are simple as bumping the version of Dispatch \(which will cause any changed dependencies to upgrade\), running data migrations, and restarting all related services.

{% hint style="info" %}
In some cases you may want to stop services before doing the upgrade process or avoid intermittent errors.
{% endhint %}

## Upgrading Dispatch

### Upgrading the package

The easiest way to upgrade the Dispatch package using`pip`:

```bash
pip install --upgrade dispatch
```

You may prefer to install a fixed version rather than just assuming the latest, as it will allow you to better understand what is changing.

If you're instlal from source, you may have additional requirements that are unfulfilled, so take the neessary precautions of testing your environment before committing to the upgrade.

### Running Migrations

Just as during the initial setup, migrations are applied with the upgrade command.

```bash
dispatch database upgrade
```

### Restarting services

You'll need to ensure that _all_ services running Dispatch code are restarted after an upgrade. This is important as Python loads modules in memory and code changes will not be reflected until a restart.

These services include:

* webserver -- `dispatch server start`
* scheduler -- `dispatch scheduler start`

