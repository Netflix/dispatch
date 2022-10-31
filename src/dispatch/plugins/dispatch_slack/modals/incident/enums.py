from dispatch.enums import DispatchEnum


# report + update blocks
class IncidentBlockId(DispatchEnum):
    description = "description_field"
    priority = "incident_priority_field"
    project = "project_field"
    resolution = "resolution_field"
    severity = "incident_severity_field"
    status = "status_field"
    tags = "tags_select_field"
    title = "title_field"
    type = "incident_type_field"


# report incident
class ReportIncidentCallbackId(DispatchEnum):
    submit_form = "report_incident_submit_form"
    update_view = "report_incident_update_view"


# update incident
class UpdateIncidentCallbackId(DispatchEnum):
    submit_form = "update_incident_submit_form"


# update participant
class UpdateParticipantBlockId(DispatchEnum):
    reason_added = "reason_added_field"
    participant = "selected_participant_field"


class UpdateParticipantCallbackId(DispatchEnum):
    submit_form = "update_participant_submit_form"
    update_view = "update_participant_update_view"


# update notification
class UpdateNotificationsGroupBlockId(DispatchEnum):
    update_members = "update_members_field"


class UpdateNotificationsGroupCallbackId(DispatchEnum):
    submit_form = "update_notifications_group_submit_form"


# add timeline
class AddTimelineEventBlockId(DispatchEnum):
    date = "date_field"
    hour = "hour_field"
    minute = "minute_field"
    timezone = "timezone_field"
    description = "description_field"


class AddTimelineEventCallbackId(DispatchEnum):
    submit_form = "add_timeline_event_submit_form"
