from dispatch.enums import DocumentResourceTypes


def deslug(document_type: DocumentResourceTypes) -> str:
    """Deslugs a document resource type."""
    return " ".join([w.capitalize() for w in document_type.split("-")[1:]])
