from dispatch.enums import DispatchEnum


class CaseNotificationActions(DispatchEnum):
    escalate = "case-notification-escalate"
    resolve = "case-notification-resolve"
    reopen = "case-notification-reopen"
    acknowledge = "case-notification-acknowledge"
    edit = "case-notification-edit"
    join_incident = "case-notification-join-incident"


class CasePaginateActions(DispatchEnum):
    list_signal_next = "case-list-signal-next"
    list_signal_previous = "case-list-signal-previous"


class CaseEditActions(DispatchEnum):
    submit = "case-notification-edit-submit"


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


class SignalNotificationActions(DispatchEnum):
    snooze = "signal-notification-snooze"
    view = "signal-notification-view"


class SignalSnoozeActions(DispatchEnum):
    preview = "case-notification-snooze-preview"
    submit = "case-notification-snooze-submit"
