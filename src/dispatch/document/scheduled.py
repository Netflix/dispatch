import logging

from schedule import every
from sqlalchemy import func

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.term import service as term_service
from dispatch.term.models import Term

from .service import get_all

log = logging.getLogger(__name__)


@scheduler.add(every(1).day, name="sync-document-terms")
@timer
@scheduled_project_task
def sync_document_terms(db_session: SessionLocal, project: Project):
    """Performs term extraction from known documents."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="storage", project_id=project.id
    )

    if not plugin:
        log.warn(
            f"Document terms not synced. No storage plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    terms = term_service.get_all(db_session=db_session, project_id=project.id).all()
    term_strings = [t.text.lower() for t in terms if t.discoverable]
    phrases = build_term_vocab(term_strings)
    matcher = build_phrase_matcher("dispatch-term", phrases)

    documents = get_all(db_session=db_session)
    for document in documents:
        mime_type = "text/plain"
        if "sheet" in document.resource_type:
            mime_type = "text/csv"

        try:
            document_text = plugin.instance.get(document.resource_id, mime_type)
        except Exception as e:
            log.warn(e)
            continue

        extracted_terms = list(set(extract_terms_from_text(document_text, matcher)))

        matched_terms = (
            db_session.query(Term)
            .filter(func.upper(Term.text).in_([func.upper(t) for t in extracted_terms]))
            .all()
        )

        if matched_terms:
            document.terms = matched_terms
            db_session.commit()
