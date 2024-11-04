from dispatch.enums import DispatchEnum


class SignalPaginateActions(DispatchEnum):
    list_signal_next = "list-signal-next"
    list_signal_previous = "list-signal-previous"


class SignalNotificationActions(DispatchEnum):
    snooze = "signal-notification-snooze"


class SignalSnoozeActions(DispatchEnum):
    preview = "signal-notification-snooze-preview"
    submit = "signal-notification-snooze-submit"


class SignalEngagementActions(DispatchEnum):
    approve = "signal-engagement-approve"
    deny = "signal-engagement-deny"
    approve_submit = "signal-engagement-approve-submit"
    deny_submit = "signal-engagement-deny-submit"
