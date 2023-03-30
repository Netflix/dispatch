from schedule import every
import logging

from sqlalchemy.orm import Session

from dispatch.decorators import scheduled_project_task
from dispatch.individual import service as individual_service
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.service import service as service_service

from .messaging import send_oncall_shift_feedback_message

log = logging.getLogger(__name__)


@scheduler.add(every(15).minutes, name="oncall-shift-feedback")
@scheduled_project_task
def oncall_shift_feedback(project: Project, db_session: Session):
    """
    Collects feedback from individuals participating in an oncall service that has health metrics enabled
    when their oncall shift ends.
    """
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="oncall"
    )

    if not oncall_plugin:
        log.warning(
            f"Skipping collection of oncall shift feedback for project {project.name}. No oncall plugin enabled."
        )
        return

    oncall_services = service_service.get_all_by_health_metrics(
        db_session=db_session, service_type=oncall_plugin.instance.slug, health_metrics=True
    )

    for oncall_service in oncall_services:
        # we get the current oncall's information
        current_oncall_info = oncall_plugin.instance.get(
            service_id=oncall_service.external_id, type="current"
        )

        # we get the time when the current oncall will end their shift
        # current_oncall_end_utc = datetime.strptime(
        #     current_oncall_info["end"], "%Y-%m-%dT%H:%M:%S%z"
        # )
        # dt_now_utc = datetime.now(timezone.utc)

        # we check if the oncall shift will end in less than 30 minutes
        # if current_oncall_end_utc - dt_now_utc < timedelta(minutes=30):
        # TODO(mvilanova): add a check to avoid asking more than once before the oncall shift ends

        # we send the current commander a direct message asking to provide mental and emotional effort
        # and number of off hours spent on incident response tasks

        individual = individual_service.get_by_email_and_project(
            db_session=db_session, email=current_oncall_info["email"], project_id=project.id
        )

        shift_start_at = current_oncall_info["start"]
        shift_end_at = current_oncall_info["end"]

        send_oncall_shift_feedback_message(
            individual=individual,
            service=oncall_service,
            shift_end_at=shift_end_at,
            shift_start_at=shift_start_at,
            db_session=db_session,
        )

        print(
            f"Requesting oncall shift feedback from {individual.name} for the {oncall_service.name} oncall service."
        )
