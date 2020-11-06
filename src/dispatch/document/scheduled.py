import logging
from datetime import datetime
from collections import defaultdict

from schedule import every
from sqlalchemy import func

from dispatch.config import DISPATCH_HELP_EMAIL
from dispatch.messaging import DOCUMENT_EVERGREEN_REMINDER
from dispatch.decorators import background_task
from dispatch.plugin import service as plugin_service
from dispatch.route import service as route_service
from dispatch.scheduler import scheduler
from dispatch.term.models import Term

from .service import get_all, get_overdue_evergreen_documents

log = logging.getLogger(__name__)


@scheduler.add(every(1).day, name="document-term-sync")
@background_task
def sync_document_terms(db_session=None):
    """Performs term extraction from known documents."""
    p = plugin_service.get_active(db_session=db_session, plugin_type="storage")

    if not p:
        log.warning("Tried to sync document terms but couldn't find any active storage plugins.")
        return

    documents = get_all(db_session=db_session)
    for doc in documents:
        log.debug(f"Processing document. Name: {doc.name}")

        try:
            if "sheet" in doc.resource_type:
                mime_type = "text/csv"
            else:
                mime_type = "text/plain"

            doc_text = p.instance.get(doc.resource_id, mime_type)
            extracted_terms = route_service.get_terms(db_session=db_session, text=doc_text)

            matched_terms = (
                db_session.query(Term)
                .filter(func.upper(Term.text).in_([func.upper(t) for t in extracted_terms]))
                .all()
            )

            log.debug(f"Extracted the following terms from {doc.weblink}. Terms: {extracted_terms}")

            if matched_terms:
                doc.terms = matched_terms
                db_session.commit()

        except Exception as e:
            # even if one document fails we don't want them to all fail
            log.exception(e)


def create_reminder(db_session, owner_email, documents, contact_fullname, contact_weblink):
    """Contains the logic for document evergreen reminders."""
    # send email
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="email")
    if not plugin:
        log.warning("Document reminder not sent, no email plugin enabled.")
        return

    message_template = DOCUMENT_EVERGREEN_REMINDER

    items = []
    for doc in documents:
        items.append(
            {
                "name": doc.name,
                "description": doc.description,
                "weblink": doc.weblink,
            }
        )

    notification_type = "document-evergreen-reminder"
    name = subject = "Document Evergreen Reminder"
    plugin.instance.send(
        owner_email,
        message_template,
        notification_type,
        name=name,
        subject=subject,
        contact_fullname=contact_fullname,
        contact_weblink=contact_weblink,
        items=items,  # plugin expect dicts
    )

    for doc in documents:
        doc.last_evergreen_reminder_at = datetime.utcnow()
        db_session.commit()


def group_documents_by_owner(documents):
    """Groups documents by owner."""
    grouped = defaultdict(lambda: [])
    for doc in documents:
        grouped[doc.evergreen_owner].append(doc)
    return grouped


@scheduler.add(every(1).day, name="document-evergreen-reminder")
@background_task
def create_evergreen_reminders(db_session=None):
    """Sends evergreen reminders for documents that have then enabled."""
    documents = get_overdue_evergreen_documents(db_session=db_session)
    log.debug(f"Documents that need reminders. NumDocuments: {len(documents)}")

    if documents:
        contact_fullname = contact_weblink = DISPATCH_HELP_EMAIL
        grouped_documents = group_documents_by_owner(documents)
        for owner, documents in grouped_documents.items():
            create_reminder(db_session, owner, documents, contact_fullname, contact_weblink)
