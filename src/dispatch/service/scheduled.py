from datetime import datetime, timedelta, timezone

from schedule import every
import logging

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task
from dispatch.individual import service as individual_service
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler

from .messaging import send_oncall_shift_feedback_message
from .service import get_all_by_health_metrics

log = logging.getLogger(__name__)


@scheduler.add(every(15).minutes, name="collect-health-metrics")
@scheduled_project_task
def collect_health_metrics(db_session: SessionLocal, project: Project):
    """
    Collects health metrics from individuals participating in an oncall service that has health metrics enabled
    when their oncall shift ends.
    """
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="oncall"
    )

    if not oncall_plugin:
        log.warning(
            f"Skipping collection of health metrics for project {project.name}. No oncall plugin enabled."
        )
        return

    oncall_services = get_all_by_health_metrics(
        db_session=db_session, service_type=oncall_plugin.instance.slug, health_metrics=True
    )

    for oncall_service in oncall_services:
        # we get the current oncall's information
        current_oncall_info = oncall_plugin.instance.get(
            service_id=oncall_service.external_id, type="current"
        )

        # we get the time when the current oncall will end their shift
        current_oncall_end_utc = datetime.strptime(
            current_oncall_info["end"], "%Y-%m-%dT%H:%M:%S%z"
        )
        dt_now_utc = datetime.now(timezone.utc)

        # we check if the oncall shift will end in less than 30 minutes
        if current_oncall_end_utc - dt_now_utc < timedelta(minutes=30):
            # TODO(mvilanova): add a check to avoid asking more than once before the oncall shift ends

            # we send the current commander a direct message asking to provide mental and emotional effort
            # and number of off hours spent on incident response tasks

            individual = individual_service.get_by_email_and_project(
                db_session=db_session, email=current_oncall_info["email"], project_id=project.id
            )

            send_oncall_shift_feedback_message(
                service=oncall_service, individual=individual, db_session=db_session
            )
