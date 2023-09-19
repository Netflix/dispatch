from dispatch.exceptions import DispatchException


class ConversationUpdateException(DispatchException):
    """Base exception for all errors related to updating conversations."""

    pass


class NoCaseConversationRelationException(ConversationUpdateException):
    def __init__(self, case_id: int):
        super().__init__(f"No relationship between case {case_id} and a conversation.")


class NoIncidentConversationRelationException(ConversationUpdateException):
    def __init__(self, incident_id: int):
        super().__init__(f"No relationship between incident {incident_id} and a conversation.")


class NoConversationPluginException(ConversationUpdateException):
    def __init__(self, msg: str = None):
        super().__init__("No conversation plugin enabled.")
