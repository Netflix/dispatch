from typing import Optional

from dispatch.database.core import SessionLocal

from .models import Storage, StorageCreate


def get(*, db_session: SessionLocal, storage_id: int) -> Optional[Storage]:
    """Fetch a storage by its storage id."""
    return db_session.query(Storage).filter(Storage.id == storage_id).one()


def get_by_resource_id(*, db_session: SessionLocal, resource_id: str) -> Optional[Storage]:
    """Fetch a storage by its resource id."""
    return db_session.query(Storage).filter(Storage.resource_id == resource_id).one()


def get_all(*, db_session: SessionLocal):
    """Fetch all storages."""
    return db_session.query(Storage)


def create(*, db_session: SessionLocal, storage_in: StorageCreate) -> Storage:
    """Creates a new storage."""
    storage = Storage(**storage_in.dict())
    db_session.add(storage)
    db_session.commit()
    return storage


def delete(*, db_session: SessionLocal, storage_id: int):
    """Deletes a storage."""
    db_session.query(Storage).filter(Storage.id == storage_id).delete()
    db_session.commit()
