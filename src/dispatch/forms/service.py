import logging
import json
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from dispatch.database.core import resolve_attr

from .models import Forms, FormsUpdate
from .scoring import calculate_score
from dispatch.document import service as document_service
from dispatch.individual import service as individual_service
from dispatch.forms.type import service as form_type_service
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service

log = logging.getLogger(__name__)


def get(*, forms_id: int, db_session: Session) -> Optional[Forms]:
    """Gets a from by its id."""
    return db_session.query(Forms).filter(Forms.id == forms_id).one_or_none()


def get_all(*, db_session: Session):
    """Gets all forms."""
    return db_session.query(Forms)


def create(*, forms_in: dict, db_session: Session, creator) -> Forms:
    """Creates form data."""

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=creator.email, project_id=forms_in["project_id"]
    )

    form = Forms(
        **forms_in,
        creator_id=individual.id,
    )

    if forms_in.get("form_type_id"):
        form_type = form_type_service.get(
            db_session=db_session, forms_type_id=forms_in["form_type_id"]
        )
        form.score = calculate_score(forms_in.get("form_data"), form_type.scoring_schema)

    db_session.add(form)
    db_session.commit()
    return form


def update(
    *,
    forms: Forms,
    forms_in: FormsUpdate,
    db_session: Session,
) -> Forms:
    """Updates a form."""
    form_data = forms.dict()
    update_data = forms_in.dict(skip_defaults=True)

    for field in form_data:
        if field in update_data:
            setattr(forms, field, update_data[field])

    forms.score = calculate_score(forms_in.form_data, forms.form_type.scoring_schema)

    db_session.commit()
    return forms


def delete(*, db_session, forms_id: int):
    """Deletes a form."""
    form = db_session.query(Forms).filter(Forms.id == forms_id).one_or_none()
    db_session.delete(form)
    db_session.commit()


def build_form_doc(form_schema: str, form_data: str) -> str:
    # Used to build the read-only answers given the questions in form_schema and the answers in form_data
    schema = json.loads(form_schema)
    data = json.loads(form_data)
    output_qa = []

    for item in schema:
        name = item["name"]
        question = item["title"]
        # find the key in form_data corresponding to this name
        answer = data.get(name)
        if answer and isinstance(answer, list) and len(answer) == 0:
            answer = ""
        # add the question and answer to the output_qa list
        if answer:
            output_qa.append(f"{question}: {answer}")

    return "\n".join(output_qa)


def export(*, db_session: Session, ids: List[int]) -> List[str]:
    """Exports forms."""
    folders = []
    # get all the forms given the ids
    forms = db_session.query(Forms).filter(Forms.id.in_(ids)).all()
    # from the forms, get all unique project ids
    project_ids = list({form.project_id for form in forms})

    for project_id in project_ids:
        # ensure there is a document plugin active
        document_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=project_id, plugin_type="document"
        )
        if not document_plugin:
            log.warning(
                f"Forms for project id ${project_id} not exported. No document plugin enabled."
            )
            continue

        storage_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=project_id, plugin_type="storage"
        )
        if not storage_plugin:
            log.warning(
                f"Forms for project id ${project_id} not exported. No storage plugin enabled."
            )
            continue

        # create a storage folder for the forms in the root project folder
        external_storage_root_id = storage_plugin.configuration.root_id

        if not external_storage_root_id:
            log.warning(
                f"Forms for project id ${project_id} not exported. No external storage root id configured."
            )
            continue

        project = project_service.get(db_session=db_session, project_id=project_id)
        if not project:
            log.warning(f"Forms for project id ${project_id} not exported. Project not found.")
            continue

        form_export_template = document_service.get_project_forms_export_template(
            db_session=db_session, project_id=project_id
        )
        if not form_export_template:
            log.warning(
                f"Forms for project id ${project_id} not exported. No form export template document configured."
            )
            continue

        # create a folder name that includes the date and time
        folder_name = f"Exported forms {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        folder = storage_plugin.instance.create_file(
            parent_id=external_storage_root_id, name=folder_name
        )
        folders.append(folder["weblink"])

        # get the subset of forms that have this project id
        project_forms = [form for form in forms if form.project_id == project_id]

        # for each form, create a document from the template and update it with the form data
        for form in project_forms:
            export_document_name = f"{form.incident.name}-{form.form_type.name}-{form.id}"
            export_document = storage_plugin.instance.copy_file(
                folder_id=folder["id"],
                file_id=form_export_template.resource_id,
                name=export_document_name,
            )
            storage_plugin.instance.move_file(
                new_folder_id=folder["id"], file_id=export_document["id"]
            )
            document_kwargs = {
                "commander_fullname": form.incident.commander.individual.name,
                "conference_challenge": resolve_attr(form.incident, "conference.challenge"),
                "conference_weblink": resolve_attr(form.incident, "conference.weblink"),
                "conversation_weblink": resolve_attr(form.incident, "conversation.weblink"),
                "description": form.incident.description,
                "document_weblink": resolve_attr(form.incident, "incident_document.weblink"),
                "name": form.incident.name,
                "priority": form.incident.incident_priority.name,
                "reported_at": form.incident.reported_at.strftime("%m/%d/%Y %H:%M:%S"),
                "closed_at": (
                    form.incident.closed_at.strftime("%m/%d/%Y %H:%M:%S")
                    if form.incident.closed_at
                    else ""
                ),
                "resolution": form.incident.resolution,
                "severity": form.incident.incident_severity.name,
                "status": form.incident.status,
                "storage_weblink": resolve_attr(form.incident, "storage.weblink"),
                "ticket_weblink": resolve_attr(form.incident, "ticket.weblink"),
                "title": form.incident.title,
                "type": form.incident.incident_type.name,
                "summary": form.incident.summary,
                "form_status": form.status,
                "form_type": form.form_type.name,
                "form_data": build_form_doc(form.form_type.form_schema, form.form_data),
                "attorney_form_data": form.attorney_form_data,
                "attorney_status": form.attorney_status,
                "attorney_questions": form.attorney_questions,
                "attorney_analysis": form.attorney_analysis,
            }
            document_plugin.instance.update(export_document["id"], **document_kwargs)

    return folders
