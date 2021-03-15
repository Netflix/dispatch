import logging

from schedule import every

from dispatch.incident import service as incident_service
from dispatch.decorators import background_task
from dispatch.incident_cost.models import IncidentCostCreate
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.incident_cost_type.models import IncidentCostTypeRead
from dispatch.scheduler import scheduler

from .service import (
    calculate_incident_response_cost,
    get_or_create,
)


log = logging.getLogger(__name__)


@scheduler.add(every(5).minutes, name="calculate-incidents-response-cost")
@background_task
def calculate_incidents_response_cost(db_session=None):
    """
    Calculates and saves the response cost for all incidents.
    """
    response_cost_type = incident_cost_type_service.get_default(db_session=db_session)
    if not response_cost_type:
        log.warning("A default cost type for response cost has not been defined.")
        return

    # we want to update the response cost of all incidents, all the time
    incidents = incident_service.get_all(db_session=db_session)
    for incident in incidents:
        try:
            # we calculate the response cost amount
            amount = calculate_incident_response_cost(incident.id, db_session)

            incident_cost_in = IncidentCostCreate(
                incident_cost_type=IncidentCostTypeRead(**response_cost_type.__dict__), amount=amount
            )

            incident_response_cost = get_or_create(
                db_session=db_session, incident_cost_in=incident_cost_in
            )

            if incident_response_cost.amount == amount:
                continue

            # we save the new incident cost amount
            incident.incident_costs.append(incident_response_cost)
            db_session.add(incident)
            db_session.commit()

            log.debug(
                f"Response cost amount for {incident.name} incident has been updated in the database."
            )

        except Exception as e:
            # we shouldn't fail to update all incidents when one fails
            log.exception(e)
