from enum import Enum


class Visibility(str, Enum):
    open = "Open"
    restricted = "Restricted"


class SearchTypes(str, Enum):
    term = "Term"
    definition = "Definition"
    individual_contact = "Individual"
    team_contact = "Team"
    service = "Service"
    policy = "Policy"
