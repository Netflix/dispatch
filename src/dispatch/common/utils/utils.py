def get_mapping_value(key, mapping):
    """Fetches key from mapping otherwise returns default."""
    return mapping.get(key, mapping["default"])
