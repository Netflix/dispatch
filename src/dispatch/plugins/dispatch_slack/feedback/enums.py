from dispatch.conversation.enums import ConversationButtonActions
from dispatch.enums import DispatchEnum


class IncidentFeedbackNotificationBlockIds(DispatchEnum):
    feedback_input = "incident-feedback-notification-feedback-input"
    rating_select = "incident-feedback-notification-rating-select"
    anonymous_checkbox = "incident-feedback-notification-anonymous-checkbox"


class IncidentFeedbackNotificationActionIds(DispatchEnum):
    feedback_input = "incident-feedback-notification-feedback-input"
    rating_select = "incident-feedback-notification-rating-select"
    anonymous_checkbox = "incident-feedback-notification-anonymous-checkbox"


class IncidentFeedbackNotificationActions(DispatchEnum):
    submit = "incident-feedback-notification-submit"
    provide = ConversationButtonActions.feedback_notification_provide


class OncallShiftFeedbackNotificationBlockIds(DispatchEnum):
    anonymous_checkbox = "oncall-shift-feedback-notification-anonymous-checkbox"
    feedback_input = "oncall-shift-feedback-notification-feedback-input"
    hours_input = "oncall-shift-feedback-notification-hours-input"
    rating_select = "oncall-shift-feedback-notification-rating-select"


class OncallShiftFeedbackNotificationActionIds(DispatchEnum):
    anonymous_checkbox = "oncall-shift-feedback-notification-anonymous-checkbox"
    feedback_input = "oncall-shift-feedback-notification-feedback-input"
    hours_input = "oncall-shift-feedback-notification-hours-input"
    rating_select = "oncall-shift-feedback-notification-rating-select"


class OncallShiftFeedbackNotificationActions(DispatchEnum):
    provide = ConversationButtonActions.oncall_shift_feedback
    submit = "oncall-shift-feedback-notification-submit"
