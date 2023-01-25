from datetime import datetime, timedelta, timezone

# from pytz import timezone as pytz_timezone
from schedule import every
import logging

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task
from dispatch.incident_role import service as incident_role_service

# from dispatch.individual import service as individual_service
from dispatch.participant_role.enums import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler


log = logging.getLogger(__name__)


@scheduler.add(every(1).hours, name="oncall-handoff")
@scheduled_project_task
def oncall_handoff(db_session: SessionLocal, project: Project):
    """Checks when the next oncall handoff is and acts accordingly."""
    incident_commander_role_policies = incident_role_service.get_all_enabled_by_role(
        db_session=db_session, role=ParticipantRoleType.incident_commander, project_id=project.id
    )

    if not incident_commander_role_policies:
        log.debug("No Incident Commander role policies defined.")
        return

    for role_policy in incident_commander_role_policies:
        oncall_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=project.id, plugin_type="oncall"
        )

        if not oncall_plugin:
            log.warning(
                f"Oncall service {role_policy.service.name} ({role_policy.service.external_id}) not resolved. No oncall plugin enabled."
            )
            continue

        # we get the current oncall's information
        current_oncall_info = oncall_plugin.instance.get(
            service_id=role_policy.service.external_id, type="current"
        )

        # we check when the current oncall shift ends
        # oncall_timezone = pytz_timezone(current_oncall_info["time_zone"])
        current_oncall_end_utc = datetime.strptime(
            current_oncall_info["end"], "%Y-%m-%dT%H:%M:%S%z"
        )
        # print(current_oncall_end_utc)
        # current_oncall_end_local = current_oncall_end_utc.astimezone(oncall_timezone)
        # print(current_oncall_end_local)

        dt_now_utc = datetime.now(timezone.utc)
        # print(dt_now_utc)
        # dt_now_local = dt_now_utc.astimezone(oncall_timezone)
        # print(dt_now_local)

        if current_oncall_end_utc - dt_now_utc > timedelta(hours=3):
            # oncall shift in more than three hours
            print(f"oncall shift in {current_oncall_end_utc - dt_now_utc}")
            continue
        else:
            # notify current commander

            # oncall_individual = individual_service.get_by_email_and_project(
            # 	  db_session=db_session, email=current_oncall_info["email"], project_id=project.id
            # )

            # we get the next oncall's information
            next_oncall_info = oncall_plugin.instance.get(
                service_id=role_policy.service.external_id, type="next"
            )

            next_oncall_start = datetime.strptime(next_oncall_info["start"], "%Y-%m-%dT%H:%M:%S%z")
            next_oncall_end = datetime.strptime(next_oncall_info["end"], "%Y-%m-%dT%H:%M:%S%z")

            if next_oncall_end - next_oncall_start > timedelta(hours=6):
                print("Taking next oncall into consideration")
            else:
                print("Not taking next oncall into consideration")

            # oncall_individual = individual_service.get_by_email_and_project(
            # 	  db_session=db_session, email=next_oncall_info["email"], project_id=project.id
            # )
            # print(oncall_individual.name)
