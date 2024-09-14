from dispatch.enums import DispatchEnum


class ParticipantRoleType(DispatchEnum):
    assignee = "Assignee"
    incident_commander = "Incident Commander"
    liaison = "Liaison"
    scribe = "Scribe"
    participant = "Participant"
    observer = "Observer"
    reporter = "Reporter"
