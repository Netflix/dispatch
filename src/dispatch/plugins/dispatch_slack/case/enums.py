from dispatch.enums import DispatchEnum


class CaseNotificationActions(DispatchEnum):
    snooze = "case-notification-snooze"
    escalate = "case-notification-escalate"
    resolve = "case-notification-resolve"
    reopen = "case-notification-reopen"
    acknowledge = "case-notification-acknowledge"
    edit = "case-notification-edit"
    join_incident = "case-notification-join-incident"


class CaseEditActions(DispatchEnum):
    submit = "case-notification-edit-submit"


class CaseSnoozeActions(DispatchEnum):
    submit = "case-notification-snooze-submit"


class CaseResolveActions(DispatchEnum):
    submit = "case-notification-resolve-submit"


class CaseEscalateActions(DispatchEnum):
    submit = "case-notification-escalate-submit"
    project_select = "case-notification-escalate-project-select"


class CaseReportActions(DispatchEnum):
    submit = "case-report-submit"
    project_select = "case-report-project-select"


class CaseShortcutCallbacks(DispatchEnum):
    report = "case-report"
