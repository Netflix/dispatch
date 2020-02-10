from typing import Optional

from .models import Conversation


def get(*, db_session, ticket_id: int) -> Optional[Conversation]:
    return db_session.query(Conversation).filter(Conversation.id == ticket_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Conversation]:
    return (
        db_session.query(Conversation).filter(Conversation.resource_id == resource_id).one_or_none()
    )


def get_by_resource_type(*, db_session, resource_type: str) -> Optional[Conversation]:
    return (
        db_session.query(Conversation)
        .filter(Conversation.resource_type == resource_type)
        .one_or_none()
    )


def get_by_channel_id(db_session, channel_id: str) -> Optional[Conversation]:
    return (
        db_session.query(Conversation).filter(Conversation.channel_id == channel_id).one_or_none()
    )


def get_all(*, db_session):
    return db_session.query(Conversation)


def create(*, db_session, **kwargs) -> Conversation:
    contact = Conversation(**kwargs)
    db_session.add(contact)
    db_session.commit()

    return contact
