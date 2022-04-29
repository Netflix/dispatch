import logging

from schedule import every

from dispatch.database.core import SessionLocal
from dispatch.incident.enums import IncidentStatus
from dispatch.incident import service as incident_service
from dispatch.decorators import scheduled_project_task
from dispatch.project.models import Project
from dispatch.incident_cost.models import IncidentCostCreate
from dispatch.incident_cost_type.models import IncidentCostTypeRead
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.scheduler import scheduler

from .service import (
    calculate_incident_response_cost,
    create,
    get_by_incident_id_and_incident_cost_type_id,
)


log = logging.getLogger(__name__)


@scheduler.add(every(5).minutes, name="calculate-incidents-response-cost")
@scheduled_project_task
def calculate_incidents_response_cost(db_session: SessionLocal, project: Project):
    """Calculates and saves the response cost for all incidents."""
    response_cost_type = incident_cost_type_service.get_default(
        db_session=db_session, project_id=project.id
    )
    if response_cost_type is None:
        log.warning(
            f"A default cost type for response cost does not exist in the {project.name} project. Response costs won't be calculated."
        )
        return

    # we only update the cost of active and stable incidents to avoid impacting older cost metrics
    # when we make changes to average cost per employee and/ or number of annual business hours.
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.stable
    )
    incidents = active_incidents + stable_incidents

    for incident in incidents:
        try:
            # we get the response cost for the given incident
            incident_response_cost = get_by_incident_id_and_incident_cost_type_id(
                db_session=db_session,
                incident_id=incident.id,
                incident_cost_type_id=response_cost_type.id,
            )

            if incident_response_cost is None:
                # we create the response cost if it doesn't exist
                incident_cost_type = IncidentCostTypeRead.from_orm(response_cost_type)
                incident_cost_in = IncidentCostCreate(
                    incident_cost_type=incident_cost_type, project=project
                )
                incident_response_cost = create(
                    db_session=db_session, incident_cost_in=incident_cost_in
                )

            # we calculate the response cost amount
            amount = calculate_incident_response_cost(incident.id, db_session)

            # we don't need to update the cost amount if it hasn't changed
            if incident_response_cost.amount == amount:
                continue

            # we save the new incident cost amount
            incident_response_cost.amount = amount
            incident.incident_costs.append(incident_response_cost)
            db_session.add(incident)
            db_session.commit()

            log.debug(
                f"Response cost amount for {incident.name} incident has been updated in the database."
            )

        except Exception as e:
            # we shouldn't fail to update all incidents when one fails
            log.exception(e)
