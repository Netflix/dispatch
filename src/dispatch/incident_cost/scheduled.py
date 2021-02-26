import logging

from schedule import every

from dispatch import service as incident_service
from dispatch.decorators import background_task
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.scheduler import scheduler

from .service import (
    calculate_incident_opportunity_cost,
    get_by_incident_id_and_incident_cost_type_id,
)


log = logging.getLogger(__name__)


@scheduler.add(every(5).minutes, name="calculate-incidents-opportunity-cost")
@background_task
def calculate_incidents_opportunity_cost(db_session=None):
    """
    Calculates and saves the opportunity cost for all incidents.
    """
    opportunity_cost_type = incident_cost_type_service.get_by_name(
        incident_cost_type_name="Opportunity Cost", db_session=db_session
    )

    # we want to update the opportunity cost of all incidents, all the time
    incidents = incident_service.get_all(db_session=db_session)
    for incident in incidents:
        try:
            incident_opportunity_cost = get_by_incident_id_and_incident_cost_type_id(
                incident_id=incident.id,
                incident_cost_type_id=opportunity_cost_type.id,
                db_session=db_session,
            )

            # we calculate the opportunity cost
            cost = calculate_incident_opportunity_cost(incident.id, db_session)

            # we don't need to update the cost if it hasn't changed
            if incident_opportunity_cost.amount == cost:
                continue

            # we save the new incident cost
            incident_opportunity_cost.amount = cost
            db_session.add(incident_opportunity_cost)
            db_session.commit()

            log.debug(
                f"Opportunity cost amount for {incident.name} incident updated in the database."
            )

        except Exception as e:
            # we shouldn't fail to update all incidents when one fails
            log.exception(e)
