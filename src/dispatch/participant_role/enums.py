from collections.abc import Iterable

from dispatch.enums import DispatchEnum


class ParticipantRoleType(DispatchEnum):
    assignee = "Assignee"
    incident_commander = "Incident Commander"
    liaison = "Liaison"
    scribe = "Scribe"
    participant = "Participant"
    observer = "Observer"
    reporter = "Reporter"

    @classmethod
    def map_case_role_to_incident_role(
        cls, case_roles: Iterable["ParticipantRoleType"]
    ) -> "ParticipantRoleType":
        role_mapping = {
            cls.reporter: cls.reporter,
            cls.assignee: cls.incident_commander,
        }

        for role in case_roles:
            if role.role in role_mapping:
                return role_mapping[role.role]

        return cls.participant
