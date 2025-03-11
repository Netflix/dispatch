import logging

from schedule import every

from sqlalchemy.orm import Session

from dispatch.decorators import scheduled_project_task, timer
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus, CostModelType
from dispatch.project.models import Project
from dispatch.scheduler import scheduler

from .service import (
    update_case_response_cost,
    get_or_create_case_response_cost_by_model_type,
)


log = logging.getLogger(__name__)


@scheduler.add(every(1).minute, name="calculate-cases-response-cost")
@timer
@scheduled_project_task
def calculate_cases_response_cost(db_session: Session, project: Project):
    """Calculates and saves the response cost for all cases."""
    cases = case_service.get_all_by_status(
        db_session=db_session, project_id=project.id, statuses=[CaseStatus.new, CaseStatus.triage]
    )

    for case in cases:
        try:
            # we get the response cost for the given case
            case_response_cost_classic = get_or_create_case_response_cost_by_model_type(
                case=case, db_session=db_session, model_type=CostModelType.classic
            )
            case_response_cost_new = get_or_create_case_response_cost_by_model_type(
                case=case, db_session=db_session, model_type=CostModelType.new
            )

            # we don't need to update the cost of closed cases if they already have a response cost and this was updated after the case was closed
            if case.status == CaseStatus.closed:
                if case_response_cost_classic:
                    if case_response_cost_classic.updated_at > case.closed_at:
                        continue
            # we don't need to update the cost of escalated cases if they already have a response cost and this was updated after the case was escalated
            if case.status == CaseStatus.escalated:
                if case_response_cost_classic:
                    if case_response_cost_classic.updated_at > case.escalated_at:
                        continue

            # we calculate the response cost amount
            results = update_case_response_cost(case, db_session)

            # we don't need to update the cost amount if it hasn't changed
            if (
                case_response_cost_classic.amount == results[CostModelType.classic]
                and case_response_cost_new.amount == results[CostModelType.new]
            ):
                continue

            # we save the new case cost amount
            case_response_cost_classic.amount = results[CostModelType.classic]
            case.case_costs.append(case_response_cost_classic)

            case_response_cost_new.amount = results[CostModelType.new]
            case.case_costs.append(case_response_cost_new)

            db_session.add(case)
            db_session.commit()
        except Exception as e:
            # we shouldn't fail to update all cases when one fails
            log.exception(e)
