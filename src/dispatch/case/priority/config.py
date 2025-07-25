default_case_priorities = [
    {
        "name": "Low",
        "description": "This case should be triaged on a best-effort basis.",
        "view_order": 1,
        "color": "#8bc34a",
        "page_assignee": False,
        "default": True,
        "enabled": True,
        "disable_delayed_message_warning": False,
    },
    {
        "name": "Medium",
        "description": "This case should be triaged within 24hrs of case creation.",
        "view_order": 2,
        "color": "#ffeb3b",
        "page_assignee": False,
        "default": False,
        "enabled": True,
        "disable_delayed_message_warning": False,
    },
    {
        "name": "High",
        "description": "This case should be triaged within 8hrs of case creation.",
        "view_order": 3,
        "color": "#ff9800",
        "page_assignee": False,
        "default": False,
        "enabled": True,
        "disable_delayed_message_warning": False,
    },
    {
        "name": "Critical",
        "description": "This case should be triaged immediately.",
        "view_order": 4,
        "color": "#e53935",
        "page_assignee": True,
        "default": False,
        "enabled": True,
        "disable_delayed_message_warning": True,
    },
    {
        "name": "Optional",
        "description": "Triage of this case is optional.",
        "view_order": 5,
        "color": "#9e9e9e",
        "page_assignee": False,
        "default": False,
        "enabled": True,
        "disable_delayed_message_warning": False,
    },
]
