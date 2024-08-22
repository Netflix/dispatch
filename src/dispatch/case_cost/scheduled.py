import logging

from schedule import every

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task, timer
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus
from dispatch.case_cost_type import service as case_cost_type_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler

from .service import (
    calculate_case_response_cost,
    get_or_create_default_case_response_cost,
)


log = logging.getLogger(__name__)


@scheduler.add(every(10).seconds, name="calculate-cases-response-cost")
@timer
@scheduled_project_task
def calculate_cases_response_cost(db_session: SessionLocal, project: Project):
    """Calculates and saves the response cost for all cases."""
    response_cost_type = case_cost_type_service.get_default(
        db_session=db_session, project_id=project.id
    )

    if response_cost_type is None:
        log.warning(
            f"A default cost type for response cost doesn't exist in the {project.name} project and organization {project.organization.name}. Response costs for cases won't be calculated."
        )
        return

    cases = case_service.get_all_by_status(db_session=db_session, project_id=project.id)

    for case in cases:
        try:
            # we get the response cost for the given case
            case_response_cost = get_or_create_default_case_response_cost(case, db_session)

            # we don't need to update the cost of closed cases if they already have a response cost and this was updated after the case was closed
            if case.status == CaseStatus.closed:
                if case_response_cost:
                    if case_response_cost.updated_at > case.closed_at:
                        continue
            # we don't need to update the cost of escalated cases if they already have a response cost and this was updated after the case was escalated
            if case.status == CaseStatus.escalated:
                if case_response_cost:
                    if case_response_cost.updated_at > case.escalated_at:
                        continue

            # we calculate the response cost amount
            amount = calculate_case_response_cost(case.id, db_session)
            # we don't need to update the cost amount if it hasn't changed
            if case_response_cost.amount == amount:
                continue

            # we save the new case cost amount
            case_response_cost.amount = amount
            case.case_costs.append(case_response_cost)
            db_session.add(case)
            db_session.commit()
        except Exception as e:
            # we shouldn't fail to update all cases when one fails
            log.exception(e)
