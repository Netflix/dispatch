import logging

from schedule import every
from sqlalchemy import func

from dispatch.decorators import background_task
from dispatch.plugin import service as plugin_service
from dispatch.route import service as route_service
from dispatch.scheduler import scheduler
from dispatch.extensions import sentry_sdk
from dispatch.term.models import Term

from .service import get_all

log = logging.getLogger(__name__)


@scheduler.add(every(1).day, name="document-term-sync")
@background_task
def sync_document_terms(db_session=None):
    """Performs term extraction from known documents."""
    documents = get_all(db_session=db_session)

    for doc in documents:
        log.debug(f"Processing document. Name: {doc.name}")
        p = plugin_service.get_active(db_session=db_session, plugin_type="storage")

        try:
            if "sheet" in doc.resource_type:
                mime_type = "text/csv"
            else:
                mime_type = "text/plain"

            doc_text = p.get(doc.resource_id, mime_type)
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
            sentry_sdk.capture_exception(e)
            log.exception(e)
