from dispatch.enums import DispatchEnum


class CaseNotificationActions(DispatchEnum):
    edit = "case-notification-edit"
    escalate = "case-notification-escalate"
    join_incident = "case-notification-join-incident"
    reopen = "case-notification-reopen"
    resolve = "case-notification-resolve"
    triage = "case-notification-triage"


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


class SignalSnoozeActions(DispatchEnum):
    preview = "case-notification-snooze-preview"
    submit = "case-notification-snooze-submit"


class SignalEngagementActions(DispatchEnum):
    approve = "signal-engagement-approve"
    deny = "signal-engagement-deny"
    approve_submit = "signal-engagement-approve-submit"
    deny_submit = "signal-engagement-deny-submit"
