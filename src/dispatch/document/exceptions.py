from dispatch.exceptions import DispatchException


class ConversationUpdateException(DispatchException):
    """Base exception for all errors related to updating conversations."""

    pass


class NoDocumentRelationError(ConversationUpdateException):
    def __init__(self, subject_id: int):
        super().__init__(f"No relationship between subject {subject_id} and a document.")
