def test_get(session, document):
    from dispatch.document.service import get

    t_document = get(db_session=session, document_id=document.id)
    assert t_document.id == document.id


def test_get_all(session, document):
    from dispatch.document.service import get_all

    t_documents = get_all(db_session=session).all()
    assert t_documents


def test_create(session, project):
    from dispatch.document.service import create
    from dispatch.document.models import DocumentCreate

    name = "XXX"
    resource_id = "XXX"
    resource_type = "XXX"
    weblink = "https://example.com/"

    document_in = DocumentCreate(
        name=name,
        resource_id=resource_id,
        resource_type=resource_type,
        weblink=weblink,
        project=project,
    )
    document = create(db_session=session, document_in=document_in)
    assert document


def test_update(session, document):
    from dispatch.document.service import update
    from dispatch.document.models import DocumentUpdate

    name = "Updated document name"

    document_in = DocumentUpdate(
        name=name,
    )
    document = update(
        db_session=session,
        document=document,
        document_in=document_in,
    )
    assert document.name == name


def test_delete(session, document):
    from dispatch.document.service import delete, get

    delete(db_session=session, document_id=document.id)
    assert not get(db_session=session, document_id=document.id)
