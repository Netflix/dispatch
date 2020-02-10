from typing import Optional

from dispatch.definition import service as definition_service

from .models import Term, TermCreate, TermUpdate


def get(*, db_session, term_id: int) -> Optional[Term]:
    return db_session.query(Term).filter(Term.id == term_id).first()


def get_by_text(*, db_session, text: str) -> Optional[Term]:
    return db_session.query(Term).filter(Term.text == text).first()


def get_all(*, db_session):
    return db_session.query(Term)


def create(*, db_session, term_in: TermCreate) -> Term:
    definitions = [
        definition_service.upsert(db_session=db_session, definition_in=d)
        for d in term_in.definitions
    ]
    term = Term(text=term_in.text, definitions=definitions)
    db_session.add(term)
    db_session.commit()
    return term


def update(*, db_session, term: Term, term_in: TermUpdate) -> Term:
    # we only allow updates to definition associations
    definitions = [
        definition_service.upsert(db_session=db_session, definition_in=d)
        for d in term_in.definitions
    ]
    term.definitions = definitions

    db_session.add(term)
    db_session.commit()
    return term


def update_or_create(*, db_session, term_in: TermCreate) -> Term:
    q = db_session.query(Term).filter(Term.text == term_in.text)

    instance = q.first()

    if instance:
        return update(db_session=db_session, term=instance, term_in=term_in)

    return create(db_session=db_session, term_in=term_in)


def get_or_create(*, db_session, term_in) -> Term:
    if term_in.id:
        q = db_session.query(Term).filter(Term.id == term_in.id)
    else:
        q = db_session.query(Term).filter_by(**term_in.dict(exclude={"definitions", "id"}))

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, term_in=term_in)


def delete(*, db_session, term_id: int):
    term = db_session.query(Term).filter(Term.id == term_id).first()
    term.definitions = []
    db_session.delete(term)
    db_session.commit()
