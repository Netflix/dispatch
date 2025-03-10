from dispatch.conversation.enums import ConversationButtonActions
from dispatch.enums import DispatchEnum


class CaseNotificationActions(DispatchEnum):
    add_user = "case-add-user"
    do_nothing = "case-do-not-add-user"
    edit = "case-notification-edit"
    escalate = "case-notification-escalate"
    investigate = "case-notification-investigate"
    invite_user_case = ConversationButtonActions.invite_user_case
    join_incident = "case-notification-join-incident"
    migrate = "case-notification-migrate"
    reopen = "case-notification-reopen"
    resolve = "case-notification-resolve"
    triage = "case-notification-triage"
    user_mfa = "case-notification-user-mfa"


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


class CaseMigrateActions(DispatchEnum):
    submit = "case-notification-migrate-submit"


class CaseReportActions(DispatchEnum):
    submit = "case-report-submit"
    project_select = "case-report-project-select"
    case_type_select = "case-report-case-type-select"
    assignee_select = "case-report-assignee-select"


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
