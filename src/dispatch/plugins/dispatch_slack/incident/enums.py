from dispatch.enums import DispatchEnum


class AddTimelineEventBlockIds(DispatchEnum):
    date = "add-timeline-event-input"
    hour = "add-timeline-event-hour"
    minute = "add-timeline-event-minute"
    timezone = "add-timeline-event-timezone"


class AddTimelineEventActionIds(DispatchEnum):
    date = "add-timeline-event-input"
    hour = "add-timeline-event-hour"
    minute = "add-timeline-event-minute"
    timezone = "add-timeline-event-timezone"


class AddTimelineEventActions(DispatchEnum):
    submit = "add-timeline-event-submit"


class TaskNotificationActions(DispatchEnum):
    pass


class TaskNotificationActionIds(DispatchEnum):
    update_status = "update-task-event"


class TaskNotificationBlockIds(DispatchEnum):
    pass


class LinkMonitorActions(DispatchEnum):
    submit = "link-monitor-submit"


class LinkMonitorActionIds(DispatchEnum):
    monitor = "link-monitor-monitor"
    ignore = "link-monitor-ignore"


class LinkMonitorBlockIds(DispatchEnum):
    monitor = "link-monitor-monitor"


class UpdateParticipantActions(DispatchEnum):
    submit = "update-participant-submit"


class UpdateParticipantActionIds(DispatchEnum):
    pass


class UpdateParticipantBlockIds(DispatchEnum):
    reason = "update-participant-reason"
    participant = "update-participant-participant"


class AssignRoleActions(DispatchEnum):
    submit = "assign-role-submit"


class AssignRoleActionIds(DispatchEnum):
    pass


class AssignRoleBlockIds(DispatchEnum):
    user = "assign-role-user"
    role = "assign-role-role"


class EngageOncallActions(DispatchEnum):
    submit = "engage-oncall-submit"


class EngageOncallActionIds(DispatchEnum):
    service = "engage-oncall-service"
    page = "engage-oncall-page"


class EngageOncallBlockIds(DispatchEnum):
    service = "engage-oncall-service"
    page = "engage-oncall-page"


class ReportTacticalActions(DispatchEnum):
    submit = "report-tactical-submit"


class ReportTacticalActionIds(DispatchEnum):
    pass


class ReportTacticalBlockIds(DispatchEnum):
    needs = "report-tactical-needs"
    actions = "report-tactical-actions"
    conditions = "report-tactical-conditions"


class ReportExecutiveActions(DispatchEnum):
    submit = "report-executive-submit"


class ReportExecutiveActionIds(DispatchEnum):
    pass


class ReportExecutiveBlockIds(DispatchEnum):
    current_status = "report-executive-current-status"
    overview = "report-executive-overview"
    next_steps = "report-executive-next-steps"


class IncidentUpdateActions(DispatchEnum):
    submit = "incident-update-submit"
    project_select = "incident-update-project-select"


class IncidentUpdateActionIds(DispatchEnum):
    tags_multi_select = "incident-update-tags-multi-select"


class IncidentUpdateBlockIds(DispatchEnum):
    tags_multi_select = "incident-update-tags-multi-select"


class IncidentReportActions(DispatchEnum):
    submit = "incident-report-submit"
    project_select = "incident-report-project-select"


class IncidentReportActionIds(DispatchEnum):
    tags_multi_select = "incident-report-tags-multi-select"


class IncidentReportBlockIds(DispatchEnum):
    tags_multi_select = "incident-report-tags-multi-select"


class UpdateNotificationGroupActions(DispatchEnum):
    submit = "update-notification-group-submit"


class UpdateNotificationGroupActionIds(DispatchEnum):
    members = "update-notification-group-members"


class UpdateNotificationGroupBlockIds(DispatchEnum):
    members = "update-notification-group-members"
