def deslug_and_capitalize_resource_type(resource_type: str) -> str:
    """Deslugs and capitalizes each word of a given resource type string."""
    return " ".join([w.capitalize() for w in resource_type.split("-")[1:]])
