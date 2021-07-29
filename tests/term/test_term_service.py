def test_get(session, term):
    from dispatch.term.service import get

    t_term = get(db_session=session, term_id=term.id)
    assert t_term.id == term.id


def test_create(session, project):
    from dispatch.term.service import create
    from dispatch.term.models import TermCreate

    text = "text"
    discoverable = True

    term_in = TermCreate(
        text=text,
        discoverable=discoverable,
        project=project,
    )
    term = create(db_session=session, term_in=term_in)
    assert term


def test_update(session, term):
    from dispatch.term.service import update
    from dispatch.term.models import TermUpdate

    text = "Updated text"

    term_in = TermUpdate(
        text=text,
    )
    term = update(
        db_session=session,
        term=term,
        term_in=term_in,
    )
    assert term.text == text


def test_delete(session, term):
    from dispatch.term.service import delete, get

    delete(db_session=session, term_id=term.id)
    assert not get(db_session=session, term_id=term.id)
