import logging
from typing import List
from datetime import datetime
from collections import defaultdict

from schedule import every
from sqlalchemy import func

from dispatch.database.core import SessionLocal
from dispatch.config import DISPATCH_HELP_EMAIL
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.messaging.strings import DOCUMENT_EVERGREEN_REMINDER
from dispatch.decorators import scheduled_project_task
from dispatch.project.models import Project
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler
from dispatch.term.models import Term
from dispatch.term import service as term_service

from .service import get_all, get_overdue_evergreen_documents
from .models import Document

log = logging.getLogger(__name__)


@scheduler.add(every(1).day, name="document-term-sync")
@scheduled_project_task
def sync_document_terms(db_session: SessionLocal, project: Project):
    """Performs term extraction from known documents."""
    p = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="storage", project_id=project.id
    )

    if not p:
        log.debug("Tried to sync document terms but couldn't find any active storage plugins.")
        return

    terms = term_service.get_all(db_session=db_session, project_id=project.id).all()
    log.debug(f"Fetched {len(terms)} terms from database.")

    term_strings = [t.text.lower() for t in terms if t.discoverable]
    phrases = build_term_vocab(term_strings)
    matcher = build_phrase_matcher("dispatch-term", phrases)

    documents = get_all(db_session=db_session)
    for doc in documents:
        log.debug(f"Processing document. Name: {doc.name}")

        try:
            if "sheet" in doc.resource_type:
                mime_type = "text/csv"
            else:
                mime_type = "text/plain"

            doc_text = p.instance.get(doc.resource_id, mime_type)
            extracted_terms = list(set(extract_terms_from_text(doc_text, matcher)))

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


def create_reminder(
    db_session: SessionLocal, project: Project, owner_email: str, documents: List[Document]
):
    """Contains the logic for document evergreen reminders."""
    # send email
    contact_fullname = contact_weblink = DISPATCH_HELP_EMAIL
    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="email", project_id=project.id
    )
    if not plugin:
        log.warning("Document reminder not sent, no email plugin enabled.")
        return

    notification_template = DOCUMENT_EVERGREEN_REMINDER

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
    name = subject = notification_text = "Document Evergreen Reminder"
    plugin.instance.send(
        owner_email,
        notification_text,
        notification_template,
        notification_type,
        name=name,
        subject=subject,
        contact_fullname=contact_fullname,
        contact_weblink=contact_weblink,
        items=items,  # plugin expect dicts
    )

    for doc in documents:
        doc.evergreen_last_reminder_at = datetime.utcnow()
        db_session.add(doc)

    db_session.commit()


def group_documents_by_owner(documents):
    """Groups documents by owner."""
    grouped = defaultdict(lambda: [])
    for doc in documents:
        grouped[doc.evergreen_owner].append(doc)
    return grouped


@scheduler.add(every(1).day.at("18:00"), name="document-evergreen-reminder")
@scheduled_project_task
def create_evergreen_reminders(db_session: SessionLocal, project: Project):
    """Sends reminders for documents that have evergreen enabled."""
    documents = get_overdue_evergreen_documents(db_session=db_session, project_id=project.id)
    log.debug(f"Documents that need reminders. NumDocuments: {len(documents)}")

    if documents:
        grouped_documents = group_documents_by_owner(documents)
        for owner, documents in grouped_documents.items():
            create_reminder(db_session, project, owner, documents)
