---
description: Make Dispatch your own by writing a plugin!
---

# Plugins

Each plugin has its interface, but in general, all plugins are structured the same way.

```bash
setup.py
dispatch_pluginname/
dispatch_pluginname/__init__.py
dispatch_pluginname/plugin.py
```

The `__init__.py` file should contain no plugin logic, and at most, a VERSION = ‘x.x.x’ line. For example, if you want to pull the version using pkg_resources \(which is what we recommend\), your file might contain:

```python
try:
    VERSION = __import__('pkg_resources') \
        .get_distribution(__name__).version
except Exception as e:
    VERSION = 'unknown'
```

Inside of `plugin.py` declare your own `Plugin` class:

```python
import dispatch_pluginname
from dispatch.plugins.base.conversation import ConversationPlugin

class PluginName(ConversationPlugin):
    title = 'Plugin Name'
    slug = 'pluginname'
    description = 'My awesome plugin!'
    version = dispatch_pluginname.VERSION

    author = 'Your Name'
    author_url = 'https://github.com/yourname/dispatch_pluginname'

    def create(self, items, **kwargs):
        return "Conversation Created"

    def add(self, items, **kwargs):
        return "User Added"

    def send(self, items, **kwargs):
        return "Message sent"
```

Register your plugin via `entry_points` by modifying your `setup.py`:

```python
setup(
    # ...
    entry_points={
       'dispatch.plugins': [
            'pluginname = dispatch_pluginname.conversations:PluginName'
        ],
    },
)
```

You can potentially package multiple plugin types in one package, say you want to create a conversation and conference plugins for the same third-party. To accomplish this, alias the plugin in entry points to point at multiple plugins within your package:

```python
setup(
    # ...
    entry_points={
        'dispatch.plugins': [
            'pluginnameconversation = dispatch_pluginname.plugin:PluginNameConversation',
            'pluginnameconference = dispatch_pluginname.plugin:PluginNameConference'
        ],
    },
)
```

Once your plugin files are in place, you can load your plugin into your instance by installing your package:

```bash
> pip install -e .
```

:::info
For more information about python packages see: [Python Packaging](https://packaging.python.org/en/latest/distributing.html)
:::
