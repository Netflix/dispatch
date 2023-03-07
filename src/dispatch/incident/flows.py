import logging

from datetime import datetime

from sqlalchemy.orm import Session

from dispatch.conference import flows as conference_flows
from dispatch.conversation import flows as conversation_flows
from dispatch.database.core import resolve_attr
from dispatch.decorators import background_task
from dispatch.document import flows as document_flows
from dispatch.enums import DocumentResourceTypes
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.group import flows as group_flows
from dispatch.group.enums import GroupType, GroupAction
from dispatch.incident import service as incident_service
from dispatch.incident.models import IncidentRead
from dispatch.individual import service as individual_service
from dispatch.participant import flows as participant_flows
from dispatch.participant import service as participant_service
from dispatch.participant.models import Participant
from dispatch.participant_role import flows as participant_role_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.report.enums import ReportTypes
from dispatch.report.messaging import send_incident_report_reminder
from dispatch.service import service as service_service
from dispatch.storage import flows as storage_flows
from dispatch.task.enums import TaskStatus
from dispatch.ticket import flows as ticket_flows

from .messaging import (
    # get_suggested_document_items,
    send_incident_closed_information_review_reminder,
    send_incident_commander_readded_notification,
    send_incident_created_notifications,
    send_incident_management_help_tips_message,
    send_incident_new_role_assigned_notification,
    send_incident_open_tasks_ephemeral_message,
    send_incident_participant_announcement_message,
    send_incident_rating_feedback_message,
    send_incident_review_document_notification,
    # send_incident_suggested_reading_messages,
    send_incident_update_notifications,
    send_incident_welcome_participant_messages,
)
from .models import Incident, IncidentStatus


log = logging.getLogger(__name__)


def get_incident_participants(
    incident: Incident, db_session: Session
) -> tuple[list[Participant | None], list[Participant | None]]:
    """
    Get additional participants (individuals and teams) based on
    incident description, type, and priority.
    """
    individual_contacts = []
    team_contacts = []

    if incident.visibility == Visibility.open:
        plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="participant"
        )
        if plugin:
            individual_contacts, team_contacts = plugin.instance.get(
                class_instance=incident,
                project_id=incident.project.id,
                db_session=db_session,
            )
            event_service.log_incident_event(
                db_session=db_session,
                source=plugin.plugin.title,
                description="Incident participants resolved",
                incident_id=incident.id,
            )
        else:
            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description="Incident participants not resolved",
                incident_id=incident.id,
            )
            log.warning("Incident participants not resolved. No participant plugin enabled.")

    return individual_contacts, team_contacts


def reactivate_incident_participants(incident: Incident, db_session: Session):
    """Reactivates all incident participants."""
    for participant in incident.participants:
        incident_add_or_reactivate_participant_flow(
            participant.individual.email, incident.id, db_session=db_session
        )

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident participants reactivated",
        incident_id=incident.id,
    )


def inactivate_incident_participants(incident: Incident, db_session: Session):
    """Inactivates all incident participants."""
    for participant in incident.participants:
        participant_flows.inactivate_participant(participant.individual.email, incident, db_session)

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident participants inactivated",
        incident_id=incident.id,
    )


@background_task
def incident_create_flow(*, organization_slug: str, incident_id: int, db_session=None):
    """Creates all resources required for new incidents."""
    # we get the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we create the incident ticket
    ticket_flows.create_incident_ticket(incident=incident, db_session=db_session)

    # we resolve individual and team participants
    individual_participants, team_participants = get_incident_participants(incident, db_session)

    # we create the tactical group
    tactical_participant_emails = [i.email for i, _ in individual_participants]
    tactical_group = group_flows.create_group(
        subject=incident,
        group_type=GroupType.tactical,
        group_participants=tactical_participant_emails,
        db_session=db_session,
    )

    # we create the notifications group
    notification_participant_emails = [t.email for t in team_participants]
    notifications_group = group_flows.create_group(
        subject=incident,
        group_type=GroupType.notifications,
        group_participants=notification_participant_emails,
        db_session=db_session,
    )

    # we create the storage folder
    storage_members = []
    if tactical_group and notifications_group:
        storage_members = [tactical_group.email, notifications_group.email]
    else:
        storage_members = tactical_participant_emails

    storage_flows.create_storage(
        subject=incident, storage_members=storage_members, db_session=db_session
    )

    # we create the incident document
    document_flows.create_document(
        subject=incident,
        document_type=DocumentResourceTypes.incident,
        document_template=incident.incident_type.incident_template_document,
        db_session=db_session,
    )

    # we create the conference room
    conference_participants = []
    if tactical_group and notifications_group:
        conference_participants = [tactical_group.email, notifications_group.email]
    else:
        conference_participants = tactical_participant_emails

    conference_flows.create_conference(
        incident=incident, participants=conference_participants, db_session=db_session
    )

    # we create the conversation
    conversation_flows.create_conversation(incident=incident, db_session=db_session)

    # we update the incident ticket
    ticket_flows.update_incident_ticket(incident_id=incident.id, db_session=db_session)

    # we update the incident document
    document_flows.update_document(
        document=incident.incident_document, project_id=incident.project.id, db_session=db_session
    )

    # we set the conversation topic
    conversation_flows.set_conversation_topic(incident, db_session)

    # we set the conversation bookmarks
    conversation_flows.add_conversation_bookmarks(incident, db_session)

    # we defer this setup for all resolved incident roles until after resources have been created
    roles = ["reporter", "commander", "liaison", "scribe"]

    user_emails = [
        resolve_attr(incident, f"{role}.individual.email")
        for role in roles
        if resolve_attr(incident, role)
    ]
    user_emails = list(dict.fromkeys(user_emails))

    for user_email in user_emails:
        # we add the participant to the tactical group
        group_flows.update_group(
            subject=incident,
            group=incident.tactical_group,
            group_action=GroupAction.add_member,
            group_member=user_email,
            db_session=db_session,
        )

        # we add the participant to the conversation
        conversation_flows.add_participants(
            incident=incident, participant_emails=[user_email], db_session=db_session
        )

        # we announce the participant in the conversation
        send_incident_participant_announcement_message(user_email, incident, db_session)

        # we send the welcome messages to the participant
        send_incident_welcome_participant_messages(user_email, incident, db_session)

        # NOTE: Temporarily disabled until an issue with the Dispatch resolver plugin is resolved
        # we send a suggested reading message to the participant
        # suggested_document_items = get_suggested_document_items(incident, db_session)
        # send_incident_suggested_reading_messages(
        #     incident, suggested_document_items, user_email, db_session
        # )

    # wait until all resources are created before adding suggested participants
    for individual, service_id in individual_participants:
        incident_add_or_reactivate_participant_flow(
            individual.email,
            incident.id,
            participant_role=ParticipantRoleType.observer,
            service_id=service_id,
            db_session=db_session,
        )

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident participants added to incident",
        incident_id=incident.id,
    )

    send_incident_created_notifications(incident, db_session)

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident notifications sent",
        incident_id=incident.id,
    )

    # we page the incident commander based on incident priority
    if incident.incident_priority.page_commander:
        if incident.commander.service:
            service_id = incident.commander.service.external_id
            oncall_plugin = plugin_service.get_active_instance(
                db_session=db_session, project_id=incident.project.id, plugin_type="oncall"
            )
            if oncall_plugin:
                oncall_plugin.instance.page(
                    service_id=service_id,
                    incident_name=incident.name,
                    incident_title=incident.title,
                    incident_description=incident.description,
                )
            else:
                log.warning("Incident commander not paged. No plugin of type oncall enabled.")
        else:
            log.warning(
                "Incident commander not paged. No relationship between commander and an oncall service."
            )

    # we send a message to the incident commander with tips on how to manage the incident
    send_incident_management_help_tips_message(incident, db_session)

    db_session.add(incident)
    db_session.commit()

    return incident


@background_task
def incident_create_stable_flow(
    *, incident_id: int, organization_slug: str = None, db_session=None
):
    """Creates all resources necessary when an incident is created with a stable status."""
    incident_create_flow(
        incident_id=incident_id, organization_slug=organization_slug, db_session=db_session
    )
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    incident_stable_status_flow(incident=incident, db_session=db_session)


@background_task
def incident_create_closed_flow(
    *, incident_id: int, organization_slug: str = None, db_session=None
):
    """Creates all resources necessary when an incident is created with a closed status."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we inactivate all participants
    inactivate_incident_participants(incident, db_session)

    # we set the stable and close times to the reported time
    incident.stable_at = incident.closed_at = incident.reported_at

    # we create the incident ticket
    ticket_flows.create_incident_ticket(incident=incident, db_session=db_session)

    # we update the incident ticket
    ticket_flows.update_incident_ticket(incident_id=incident.id, db_session=db_session)

    db_session.add(incident)
    db_session.commit()


def incident_active_status_flow(incident: Incident, db_session=None):
    """Runs the incident active flow."""
    # we un-archive the conversation
    conversation_flows.unarchive_conversation(incident=incident, db_session=db_session)


def incident_stable_status_flow(incident: Incident, db_session=None):
    """Runs the incident stable flow."""
    # we set the stable time
    incident.stable_at = datetime.utcnow()
    db_session.add(incident)
    db_session.commit()

    if incident.incident_document:
        # we update the incident document
        document_flows.update_document(
            document=incident.incident_document,
            project_id=incident.project.id,
            db_session=db_session,
        )

    if incident.incident_review_document:
        log.info("The post-incident review document has already been created. Skipping creation...")
        return

    # we create the post-incident review document
    document_flows.create_document(
        subject=incident,
        document_type=DocumentResourceTypes.review,
        document_template=incident.incident_type.review_template_document,
        db_session=db_session,
    )

    # we update the post-incident review document
    document_flows.update_document(
        document=incident.incident_review_document,
        project_id=incident.project.id,
        db_session=db_session,
    )

    if incident.incident_review_document and incident.conversation:
        # we send a notification about the incident review document to the conversation
        send_incident_review_document_notification(
            incident.conversation.channel_id,
            incident.incident_review_document.weblink,
            incident,
            db_session,
        )

        # we bookmark the incident review document in the conversation
        conversation_flows.add_conversation_bookmark(
            incident=incident, resource=incident.incident_review_document, db_session=db_session
        )


def incident_closed_status_flow(incident: Incident, db_session=None):
    """Runs the incident closed flow."""
    # we inactivate all participants
    inactivate_incident_participants(incident, db_session)

    # we set the closed time
    incident.closed_at = datetime.utcnow()
    db_session.add(incident)
    db_session.commit()

    # we archive the conversation
    conversation_flows.archive_conversation(incident=incident, db_session=db_session)

    if incident.visibility == Visibility.open:
        storage_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="storage"
        )
        if storage_plugin:
            if storage_plugin.configuration.open_on_close:
                # we add organization wide permission to the incident document as
                # typically that's the only resource that requires it.
                try:
                    storage_plugin.instance.open(incident.incident_document.resource_id)
                except Exception as e:
                    event_service.log_incident_event(
                        db_session=db_session,
                        source="Dispatch Core App",
                        description=f"Opening incident document to anyone in the domain failed. Reason: {e}",
                        incident_id=incident.id,
                    )
                    log.exception(e)
                else:
                    event_service.log_incident_event(
                        db_session=db_session,
                        source="Dispatch Core App",
                        description="Incident document opened to anyone in the domain",
                        incident_id=incident.id,
                    )

            if storage_plugin.configuration.read_only:
                # unfortunately this can't be applied at the folder level
                # so we just mark the incident doc as readonly.
                try:
                    storage_plugin.instance.mark_readonly(incident.incident_document.resource_id)
                except Exception as e:
                    event_service.log_incident_event(
                        db_session=db_session,
                        source="Dispatch Core App",
                        description=f"Marking incident document as readonly failed. Reason: {e}",
                        incident_id=incident.id,
                    )
                    log.exception(e)
                else:
                    event_service.log_incident_event(
                        db_session=db_session,
                        source="Dispatch Core App",
                        description="Incident document marked as readonly",
                        incident_id=incident.id,
                    )

    # we send a direct message to the incident commander asking to review
    # the incident's information and to tag the incident if appropiate
    send_incident_closed_information_review_reminder(incident, db_session)

    # we send a direct message to all participants asking them
    # to rate and provide feedback about the incident
    send_incident_rating_feedback_message(incident, db_session)


def conversation_topic_dispatcher(
    user_email: str,
    incident: Incident,
    previous_incident: dict,
    db_session: Session,
):
    """Determines if the conversation topic needs to be updated."""
    # we load the individual
    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=user_email, project_id=incident.project.id
    )

    conversation_topic_change = False
    if previous_incident.title != incident.title:
        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f'{individual.name} changed the incident title to "{incident.title}"',
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.description != incident.description:
        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident description",
            details={"description": incident.description},
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_type.name != incident.incident_type.name:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident type to {incident.incident_type.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_severity.name != incident.incident_severity.name:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident severity to {incident.incident_severity.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_priority.name != incident.incident_priority.name:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident priority to {incident.incident_priority.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.status != incident.status:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} marked the incident as {incident.status.lower()}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if conversation_topic_change:
        if incident.status != IncidentStatus.closed:
            conversation_flows.set_conversation_topic(incident, db_session)


def status_flow_dispatcher(
    incident: Incident,
    current_status: IncidentStatus,
    previous_status: IncidentStatus,
    db_session: Session,
):
    """Runs the correct flows depending on the incident's current and previous status."""
    # we have a currently active incident
    if current_status == IncidentStatus.active:
        if previous_status == IncidentStatus.closed:
            # re-activate incident
            incident_active_status_flow(incident=incident, db_session=db_session)
            reactivate_incident_participants(incident=incident, db_session=db_session)
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)
        elif previous_status == IncidentStatus.stable:
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)

    # we currently have a stable incident
    elif current_status == IncidentStatus.stable:
        if previous_status == IncidentStatus.active:
            incident_stable_status_flow(incident=incident, db_session=db_session)
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)
        elif previous_status == IncidentStatus.closed:
            incident_active_status_flow(incident=incident, db_session=db_session)
            incident_stable_status_flow(incident=incident, db_session=db_session)
            reactivate_incident_participants(incident=incident, db_session=db_session)
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)

    # we currently have a closed incident
    elif current_status == IncidentStatus.closed:
        if previous_status == IncidentStatus.active:
            incident_stable_status_flow(incident=incident, db_session=db_session)
            incident_closed_status_flow(incident=incident, db_session=db_session)
        elif previous_status == IncidentStatus.stable:
            incident_closed_status_flow(incident=incident, db_session=db_session)

    if previous_status != current_status:
        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"The incident status has been changed from {previous_status.lower()} to {current_status.lower()}",  # noqa
            incident_id=incident.id,
        )


@background_task
def incident_update_flow(
    user_email: str,
    commander_email: str,
    reporter_email: str,
    incident_id: int,
    previous_incident: IncidentRead,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the incident update flow."""
    # we load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident.commander.individual.email != commander_email:
        # we assign the commander role to another participant
        incident_assign_role_flow(
            incident_id=incident_id,
            assigner_email=user_email,
            assignee_email=commander_email,
            assignee_role=ParticipantRoleType.incident_commander,
            db_session=db_session,
        )

    if incident.reporter.individual.email != reporter_email:
        # we assign the reporter role to another participant
        incident_assign_role_flow(
            incident_id=incident_id,
            assigner_email=user_email,
            assignee_email=reporter_email,
            assignee_role=ParticipantRoleType.reporter,
            db_session=db_session,
        )

    # we run the active, stable or closed flows based on incident status change
    status_flow_dispatcher(incident, incident.status, previous_incident.status, db_session)

    # we update the conversation topic
    conversation_topic_dispatcher(user_email, incident, previous_incident, db_session)

    # we update the external ticket
    ticket_flows.update_incident_ticket(incident_id=incident.id, db_session=db_session)

    if incident.status == IncidentStatus.active:
        # we re-resolve and add individuals to the incident
        individual_participants, team_participants = get_incident_participants(incident, db_session)

        for individual, service_id in individual_participants:
            incident_add_or_reactivate_participant_flow(
                individual.email,
                incident.id,
                participant_role=ParticipantRoleType.observer,
                service_id=service_id,
                db_session=db_session,
            )

        # we add the team distributions lists to the notifications group
        # we only have to do this for teams as new members
        # will be added to the tactical group on incident join
        group_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
        )
        if group_plugin:
            team_participant_emails = [x.email for x in team_participants]
            group_plugin.instance.add(incident.notifications_group.email, team_participant_emails)

    # we send the incident update notifications
    send_incident_update_notifications(incident, previous_incident, db_session)


def incident_assign_role_flow(
    incident_id: int,
    assigner_email: str,
    assignee_email: str,
    assignee_role: str,
    db_session: Session,
):
    """Runs the incident participant role assignment flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we add the assignee to the incident if they're not a participant
    incident_add_or_reactivate_participant_flow(assignee_email, incident.id, db_session=db_session)

    # we run the participant assign role flow
    result = participant_role_flows.assign_role_flow(
        incident, assignee_email, assignee_role, db_session
    )

    if result == "assignee_has_role":
        # NOTE: This is disabled until we can determine the source of the caller
        # we let the assigner know that the assignee already has this role
        # send_incident_participant_has_role_ephemeral_message(
        #   assigner_email, assignee_contact_info, assignee_role, incident
        # )
        return

    if result == "role_not_assigned":
        # NOTE: This is disabled until we can determine the source of the caller
        # we let the assigner know that we were not able to assign the role
        # send_incident_participant_role_not_assigned_ephemeral_message(
        #   assigner_email, assignee_contact_info, assignee_role, incident
        # )
        return

    if incident.status != IncidentStatus.closed:
        if assignee_role != ParticipantRoleType.participant:
            # we resolve the assigner and assignee contact information
            contact_plugin = plugin_service.get_active_instance(
                db_session=db_session, project_id=incident.project.id, plugin_type="contact"
            )

            if contact_plugin:
                assigner_contact_info = contact_plugin.instance.get(
                    assigner_email, db_session=db_session
                )
                assignee_contact_info = contact_plugin.instance.get(
                    assignee_email, db_session=db_session
                )
            else:
                assigner_contact_info = {
                    "email": assigner_email,
                    "fullname": "Unknown",
                    "weblink": "",
                }
                assignee_contact_info = {
                    "email": assignee_email,
                    "fullname": "Unknown",
                    "weblink": "",
                }

            # we send a notification to the incident conversation
            send_incident_new_role_assigned_notification(
                assigner_contact_info, assignee_contact_info, assignee_role, incident, db_session
            )

        if assignee_role == ParticipantRoleType.incident_commander:
            # we update the conversation topic
            conversation_flows.set_conversation_topic(incident, db_session)

            # we send a message to the incident commander with tips on how to manage the incident
            send_incident_management_help_tips_message(incident, db_session)


@background_task
def incident_engage_oncall_flow(
    user_email: str,
    incident_id: int,
    oncall_service_external_id: str,
    page=None,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the incident engage oncall flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we resolve the oncall service
    oncall_service = service_service.get_by_external_id_and_project_id(
        db_session=db_session,
        external_id=oncall_service_external_id,
        project_id=incident.project.id,
    )

    # we get the active oncall plugin
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="oncall"
    )

    if oncall_plugin:
        if oncall_plugin.plugin.slug != oncall_service.type:
            log.warning(
                f"Unable to engage the oncall. Oncall plugin enabled not of type {oncall_plugin.plugin.slug}."  # noqa
            )
            return None, None
    else:
        log.warning("Unable to engage the oncall. No oncall plugins enabled.")
        return None, None

    oncall_email = oncall_plugin.instance.get(service_id=oncall_service_external_id)

    # we attempt to add the oncall to the incident
    oncall_participant_added = incident_add_or_reactivate_participant_flow(
        oncall_email, incident.id, service_id=oncall_service.id, db_session=db_session
    )

    if not oncall_participant_added:
        # we already have the oncall for the service in the incident
        return None, oncall_service

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=user_email, project_id=incident.project.id
    )

    event_service.log_incident_event(
        db_session=db_session,
        source=oncall_plugin.plugin.title,
        description=f"{individual.name} engages oncall service {oncall_service.name}",
        incident_id=incident.id,
    )

    if page == "Yes":
        # we page the oncall
        oncall_plugin.instance.page(
            service_id=oncall_service_external_id,
            incident_name=incident.name,
            incident_title=incident.title,
            incident_description=incident.description,
        )

        event_service.log_incident_event(
            db_session=db_session,
            source=oncall_plugin.plugin.title,
            description=f"{oncall_service.name} on-call paged",
            incident_id=incident.id,
        )

    return oncall_participant_added.individual, oncall_service


@background_task
def incident_subscribe_participant_flow(
    user_email: str,
    incident_id: int,
    organization_slug: str,
    db_session=None,
):
    """Subscribes a participant to the incident."""
    # we get the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we add the participant to the tactical group
    group_flows.update_group(
        subject=incident,
        group=incident.tactical_group,
        group_action=GroupAction.add_member,
        group_member=user_email,
        db_session=db_session,
    )


@background_task
def incident_add_or_reactivate_participant_flow(
    user_email: str,
    incident_id: int,
    participant_role: ParticipantRoleType = ParticipantRoleType.participant,
    service_id: int = 0,
    event: dict = None,
    organization_slug: str = None,
    db_session=None,
) -> Participant:
    """Runs the incident add or reactivate participant flow."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if service_id:
        # we need to ensure that we don't add another member of a service if one
        # already exists (e.g. overlapping oncalls, we assume they will hand-off if necessary)
        participant = participant_service.get_by_incident_id_and_service_id(
            incident_id=incident_id, service_id=service_id, db_session=db_session
        )

        if participant:
            log.info("Skipping resolved participant. Oncall service member already engaged.")
            return

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=user_email
    )

    if participant:
        if participant.active_roles:
            return participant

        if incident.status != IncidentStatus.closed:
            # we reactivate the participant
            participant_flows.reactivate_participant(
                user_email, incident, db_session, service_id=service_id
            )
    else:
        # we add the participant to the incident
        participant = participant_flows.add_participant(
            user_email, incident, db_session, service_id=service_id, role=participant_role
        )

    # we add the participant to the tactical group
    group_flows.update_group(
        subject=incident,
        group=incident.tactical_group,
        group_action=GroupAction.add_member,
        group_member=user_email,
        db_session=db_session,
    )

    if incident.status != IncidentStatus.closed:
        # we add the participant to the conversation
        conversation_flows.add_participants(
            incident=incident, participant_emails=[user_email], db_session=db_session
        )

        # we announce the participant in the conversation
        send_incident_participant_announcement_message(user_email, incident, db_session)

        # we send the welcome messages to the participant
        send_incident_welcome_participant_messages(user_email, incident, db_session)

        # NOTE: Temporarily disabled until an issue with the Dispatch resolver plugin is resolved
        # we send a suggested reading message to the participant
        # suggested_document_items = get_suggested_document_items(incident, db_session)
        # send_incident_suggested_reading_messages(
        #     incident, suggested_document_items, user_email, db_session
        # )

    return participant


@background_task
def incident_remove_participant_flow(
    user_email: str,
    incident_id: int,
    event: dict = None,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the remove participant flow."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=user_email
    )

    for task in incident.tasks:
        if task.status == TaskStatus.open:
            for assignee in task.assignees:
                if assignee == participant:
                    # we add the participant to the conversation
                    conversation_flows.add_participants(
                        incident=incident, participant_emails=[user_email], db_session=db_session
                    )

                    # we ask the participant to resolve or re-assign
                    # their tasks before leaving the incident conversation
                    send_incident_open_tasks_ephemeral_message(user_email, incident, db_session)

                    return

    if user_email == incident.commander.individual.email:
        # we add the participant to the conversation
        conversation_flows.add_participants(
            incident=incident, participant_emails=[user_email], db_session=db_session
        )

        # we send a notification to the channel
        send_incident_commander_readded_notification(incident, db_session)

        return

    # we remove the participant from the incident
    participant_flows.remove_participant(user_email, incident, db_session)

    # we remove the participant from the tactical group
    group_flows.update_group(
        subject=incident,
        group=incident.tactical_group,
        group_action=GroupAction.remove_member,
        group_member=user_email,
        db_session=db_session,
    )
