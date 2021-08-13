def test_get(session, storage):
    from dispatch.storage.service import get

    t_storage = get(db_session=session, storage_id=storage.id)
    assert t_storage.id == storage.id


def test_get_all(session, storages):
    from dispatch.storage.service import get_all

    t_storages = get_all(db_session=session).all()
    assert t_storages


def test_create(session, project):
    from dispatch.storage.service import create
    from dispatch.storage.models import StorageCreate

    resource_id = "resource_id"
    resource_type = "resource_type"
    weblink = "https://www.example.com/"

    storage_in = StorageCreate(
        resource_id=resource_id,
        resource_type=resource_type,
        weblink=weblink,
    )
    storage = create(db_session=session, storage_in=storage_in)
    assert storage
