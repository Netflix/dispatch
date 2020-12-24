def create_pydantic_include(include):
    """Creates a pydantic sets based on dotted notation."""
    include_sets = {}
    for i in include:
        keyset = None
        for key in reversed(i.split(".")):
            if keyset:
                keyset = {key: keyset}
            else:
                keyset = {key: ...}
        include_sets.update(keyset)

    return include_sets
