import logging

from datetime import date

from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.decorators import background_task
from dispatch.document import service as document_service
from dispatch.document.models import DocumentCreate
from dispatch.enums import DocumentResourceTypes
from dispatch.event import service as event_service
from dispatch.exceptions import InvalidConfigurationError
from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service
from dispatch.plugin import service as plugin_service

from .enums import ReportTypes
from .messaging import (
    send_executive_report_to_notifications_group,
    send_tactical_report_to_conversation,
    send_tactical_report_to_tactical_group,
)
from .models import ReportCreate, TacticalReportCreate, ExecutiveReportCreate
from .service import create, get_all_by_incident_id_and_type


log = logging.getLogger(__name__)


@background_task
def create_tactical_report(
    user_email: str,
    incident_id: int,
    tactical_report_in: TacticalReportCreate,
    organization_slug: str = None,
    db_session=None,
):
    """Creates and sends a new tactical report to a conversation."""
    conditions = tactical_report_in.conditions
    actions = tactical_report_in.actions
    needs = tactical_report_in.needs

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we create a new tactical report
    details = {"conditions": conditions, "actions": actions, "needs": needs}
    tactical_report_in = ReportCreate(details=details, type=ReportTypes.tactical_report)
    tactical_report = create(db_session=db_session, report_in=tactical_report_in)

    # we load the participant
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # we save the tactical report
    participant.reports.append(tactical_report)
    incident.reports.append(tactical_report)

    db_session.add(participant)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Incident Participant",
        description=f"{participant.individual.name} created a new tactical report",
        details={"conditions": conditions, "actions": actions, "needs": needs},
        incident_id=incident_id,
        individual_id=participant.individual.id,
    )

    # we send the tactical report to the conversation
    send_tactical_report_to_conversation(incident_id, conditions, actions, needs, db_session)

    # we send the tactical report to the tactical group
    send_tactical_report_to_tactical_group(incident_id, tactical_report, db_session)

    return tactical_report


@background_task
def create_executive_report(
    user_email: str,
    incident_id: int,
    executive_report_in: ExecutiveReportCreate,
    organization_slug: str = None,
    db_session=None,
):
    """Creates an executive report."""
    current_date = date.today().strftime("%B %d, %Y")

    current_status = executive_report_in.current_status
    overview = executive_report_in.overview
    next_steps = executive_report_in.next_steps

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if not incident.incident_type.executive_template_document:
        raise ValidationError(
            [
                ErrorWrapper(
                    InvalidConfigurationError(msg="No executive report template defined."),
                    loc="executive_template_document",
                )
            ],
            model=ExecutiveReportCreate,
        )

    # we fetch all previous executive reports
    executive_reports = get_all_by_incident_id_and_type(
        db_session=db_session, incident_id=incident_id, report_type=ReportTypes.executive_report
    )

    previous_executive_reports = []
    for executive_report in executive_reports:
        previous_executive_reports.append(
            f"{executive_report.document.name} - {executive_report.document.weblink}\n"
        )

    # we create a new executive report
    details = {"current_status": current_status, "overview": overview, "next_steps": next_steps}
    executive_report_in = ReportCreate(
        details=details,
        type=ReportTypes.executive_report,
    )
    executive_report = create(db_session=db_session, report_in=executive_report_in)

    # we load the participant
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # we save the executive report
    participant.reports.append(executive_report)
    incident.reports.append(executive_report)

    db_session.add(participant)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Incident Participant",
        description=f"{participant.individual.name} created a new executive report",
        details={"current_status": current_status, "overview": overview, "next_steps": next_steps},
        incident_id=incident_id,
        individual_id=participant.individual.id,
    )

    # we create a new document for the executive report
    storage_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="storage"
    )
    executive_report_document_name = f"{incident.name} - Executive Report - {current_date}"
    executive_report_document = storage_plugin.instance.copy_file(
        folder_id=incident.storage.resource_id,
        file_id=incident.incident_type.executive_template_document.resource_id,
        name=executive_report_document_name,
    )

    executive_report_document.update(
        {
            "name": executive_report_document_name,
            "description": incident.incident_type.executive_template_document.description,
            "resource_type": DocumentResourceTypes.executive,
        }
    )

    storage_plugin.instance.move_file(
        new_folder_id=incident.storage.resource_id, file_id=executive_report_document["id"]
    )

    event_service.log(
        db_session=db_session,
        source=storage_plugin.plugin.title,
        description="Executive report document added to storage",
        incident_id=incident.id,
    )

    document_in = DocumentCreate(
        name=executive_report_document["name"],
        description=executive_report_document["description"],
        resource_id=executive_report_document["id"],
        resource_type=executive_report_document["resource_type"],
        project=incident.project,
        weblink=executive_report_document["weblink"],
    )
    executive_report.document = document_service.create(
        db_session=db_session, document_in=document_in
    )

    incident.documents.append(executive_report.document)

    db_session.add(executive_report)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Executive report document added to incident",
        incident_id=incident.id,
    )

    # we update the incident update document
    document_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="document"
    )
    document_plugin.instance.update(
        executive_report_document["id"],
        name=incident.name,
        title=incident.title,
        current_date=current_date,
        current_status=current_status,
        overview=overview,
        next_steps=next_steps,
        previous_reports="\n".join(previous_executive_reports),
        commander_fullname=incident.commander.individual.name,
        commander_team=incident.commander.team,
        commander_weblink=incident.commander.individual.weblink,
    )

    # we send the executive report to the notifications group
    send_executive_report_to_notifications_group(incident.id, executive_report, db_session)

    return executive_report
