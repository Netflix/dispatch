from dispatch.enums import Visibility

default_incident_type = {
    "name": "Default",
    "description": "This is the default incident type.",
    "visibility": Visibility.open,
    "exclude_from_metrics": False,
    "default": True,
    "enabled": True,
}
