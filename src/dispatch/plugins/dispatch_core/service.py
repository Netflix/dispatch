import re


def create_resource_id(title: str) -> str:
    """Creates a Slack-friendly resource id from the incident title."""
    resource_id = title.lower()

    # Replace any character that is not a lowercase letter or number with a hyphen
    resource_id = re.sub(r"[^a-z0-9]", "-", resource_id)

    # Replace multiple consecutive hyphens with a single hyphen
    resource_id = re.sub(r"-+", "-", resource_id)

    # Ensure the channel name is not longer than 80 characters
    resource_id = resource_id[:80]

    # Remove leading or trailing hyphens
    resource_id = resource_id.strip("-")

    return resource_id
