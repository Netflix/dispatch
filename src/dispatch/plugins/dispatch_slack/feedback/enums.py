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
    feedback_input = "oncall-shift-feedback-notification-feedback-input"
    rating_select = "oncall-shift-feedback-notification-rating-select"
    anonymous_checkbox = "oncall-shift-feedback-notification-anonymous-checkbox"


class OncallShiftFeedbackNotificationActionIds(DispatchEnum):
    feedback_input = "oncall-shift-feedback-notification-feedback-input"
    rating_select = "oncall-shift-feedback-notification-rating-select"
    anonymous_checkbox = "oncall-shift-feedback-notification-anonymous-checkbox"


class OncallShiftFeedbackNotificationActions(DispatchEnum):
    submit = "oncall-shift-feedback-notification-submit"
    provide = ConversationButtonActions.oncall_shift_feedback
