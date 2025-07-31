import logging
from sqlalchemy.orm import Session

from dispatch.project import service as project_service
from dispatch.ai.enums import GenAIType
from .models import Prompt, PromptCreate, PromptUpdate

log = logging.getLogger(__name__)


def get(*, prompt_id: int, db_session: Session) -> Prompt | None:
    """Gets a prompt by its id."""
    return db_session.query(Prompt).filter(Prompt.id == prompt_id).one_or_none()


def get_by_type(*, genai_type: int, project_id: int, db_session: Session) -> Prompt | None:
    """Gets an enabled prompt by its type."""
    return (
        db_session.query(Prompt)
        .filter(Prompt.project_id == project_id)
        .filter(Prompt.genai_type == genai_type)
        .filter(Prompt.enabled)
        .first()
    )


def get_all(*, db_session: Session) -> list[Prompt | None]:
    """Gets all prompts."""
    return db_session.query(Prompt)


def create(*, prompt_in: PromptCreate, db_session: Session) -> Prompt:
    """Creates prompt data."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=prompt_in.project
    )

    # If this prompt is being enabled, check if another enabled prompt of the same type exists
    if prompt_in.enabled:
        existing_enabled = (
            db_session.query(Prompt)
            .filter(Prompt.project_id == project.id)
            .filter(Prompt.genai_type == prompt_in.genai_type)
            .filter(Prompt.enabled)
            .first()
        )
        if existing_enabled:
            type_name = GenAIType(prompt_in.genai_type).display_name
            raise ValueError(
                f"Another prompt of type '{type_name}' is already enabled for this project. "
                "Only one prompt per type can be enabled."
            )

    prompt = Prompt(**prompt_in.dict(exclude={"project"}), project=project)

    db_session.add(prompt)
    db_session.commit()
    return prompt


def update(
    *,
    prompt: Prompt,
    prompt_in: PromptUpdate,
    db_session: Session,
) -> Prompt:
    """Updates a prompt."""
    update_data = prompt_in.dict(exclude_unset=True)

    # If this prompt is being enabled, check if another enabled prompt of the same type exists
    if update_data.get("enabled", False):
        existing_enabled = (
            db_session.query(Prompt)
            .filter(Prompt.project_id == prompt.project_id)
            .filter(Prompt.genai_type == prompt.genai_type)
            .filter(Prompt.enabled)
            .filter(Prompt.id != prompt.id)  # Exclude current prompt
            .first()
        )
        if existing_enabled:
            type_name = GenAIType(prompt.genai_type).display_name
            raise ValueError(
                f"Another prompt of type '{type_name}' is already enabled for this project. "
                "Only one prompt per type can be enabled."
            )

    # Update only the fields that were provided in the update data
    for field, value in update_data.items():
        setattr(prompt, field, value)

    db_session.commit()
    return prompt


def delete(*, db_session, prompt_id: int):
    """Deletes a prompt."""
    prompt = db_session.query(Prompt).filter(Prompt.id == prompt_id).one_or_none()
    db_session.delete(prompt)
    db_session.commit()
