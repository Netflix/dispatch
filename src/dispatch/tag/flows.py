from .models import Tag


def check_for_tag_change(
    previous_incident_tags: list[Tag], current_incident_tags: list[Tag]
) -> tuple[str, dict]:
    """Determines if there is any tag change and builds the description string and details if so"""
    added_tags = []
    removed_tags = []
    description = ""
    details = {}

    for tag in previous_incident_tags:
        if tag.id not in [t.id for t in current_incident_tags]:
            removed_tags.append(f"{tag.tag_type.name}/{tag.name}")

    for tag in current_incident_tags:
        if tag.id not in [t.id for t in previous_incident_tags]:
            added_tags.append(f"{tag.tag_type.name}/{tag.name}")

    if added_tags:
        description = f"added {len(added_tags)} tag{'s' if len(added_tags) > 1 else ''}"
        details.update({"added tags": ", ".join(added_tags)})
        if removed_tags:
            description += " and "
    if removed_tags:
        description += f"removed {len(removed_tags)} tag{'s' if len(removed_tags) > 1 else ''}"
        details.update({"removed tags": ", ".join(removed_tags)})

    return (description, details)
