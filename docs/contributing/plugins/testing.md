---
description: How to test your plugins.
---

# Testing

Dispatch provides a basic py.test based testing framework for plugins. In a simply plugin you'll need to do a few things to get it working:

## Require Dispatch

Augment your plugin's `setup.py` to ensure that it depends on `dispatch`

```python
setup(
    # ...
    install_requires=[
       'dispatch',
    ]
)
```

## Running Tests

Running tests follows the py.test standard. As long as your test files and methods are named appropriately \(`test_filename.py` and `test_function()`\) you can simply call out to py.test:

