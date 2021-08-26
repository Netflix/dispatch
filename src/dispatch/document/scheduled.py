import logging

from schedule import every
from sqlalchemy import func

from dispatch.database.core import SessionLocal
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.decorators import scheduled_project_task
from dispatch.project.models import Project
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler
from dispatch.term.models import Term
from dispatch.term import service as term_service

from .service import get_all

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
