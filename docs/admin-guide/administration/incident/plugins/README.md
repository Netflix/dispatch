---
description: Plugin Configurations
---

# Plugins

Much of Dispatch's functionality comes from its plugins. The current Dispatch web UI is limited to enabling and disabling plugins on a per-project basis. To make modifications to how plugins behave or are configured, changes must be deployed via the server configuration file. See the [server](../../server.md) configuration documentation for more infomation.

By default, no plugins are _required_ to create an incident. As you enable plugins, they will be additive to the incident process (e.g., creating slack channels, google docs, etc.)

![](../../../../.gitbook/assets/admin-ui-incident-plugins.png)

Looking to add your own functionality to Dispatch via plugins? See the [contributing](../../../../contributing/plugins/README.md) documentation.
