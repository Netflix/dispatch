from dispatch.enums import DispatchEnum


class ParticipantRoleType(DispatchEnum):
    incident_commander = "Incident Commander"
    liaison = "Liaison"
    observer = "Observer"
    participant = "Participant"
    reporter = "Reporter"
    scribe = "Scribe"
