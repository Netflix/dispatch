
from sqlalchemy.orm import Session

from .models import Storage, StorageCreate


def get(*, db_session: Session, storage_id: int) -> Storage | None:
    """Gets a storage by its storage id."""
    return db_session.query(Storage).filter(Storage.id == storage_id).one()


def get_by_resource_id(*, db_session: Session, resource_id: str) -> Storage | None:
    """Gets a storage by its resource id."""
    return db_session.query(Storage).filter(Storage.resource_id == resource_id).one()


def get_all(*, db_session: Session):
    """Gets all storages."""
    return db_session.query(Storage)


def create(*, db_session: Session, storage_in: StorageCreate) -> Storage:
    """Creates a storage."""
    storage = Storage(**storage_in.dict())
    db_session.add(storage)
    db_session.commit()
    return storage


def delete(*, db_session: Session, storage_id: int):
    """Deletes a storage."""
    db_session.query(Storage).filter(Storage.id == storage_id).delete()
    db_session.commit()
