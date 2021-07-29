from typing import Optional

from .models import Storage, StorageCreate


def get(*, db_session, storage_id: int) -> Optional[Storage]:
    """Fetch a storage by its storage id."""
    return db_session.query(Storage).filter(Storage.id == storage_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Storage]:
    """Fetch a storage by its resource id."""
    return db_session.query(Storage).filter(Storage.resource_id == resource_id).one()


def get_all(*, db_session):
    """Fetch all storages."""
    return db_session.query(Storage)


def create(*, db_session, storage_in: StorageCreate) -> Storage:
    """Create a new storage."""
    storage = Storage(**storage_in.dict())
    db_session.add(storage)
    db_session.commit()
    return storage
