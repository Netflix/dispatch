from dispatch.conversation.enums import ConversationButtonActions
from dispatch.enums import DispatchEnum


class IncidentFeedbackNotificationBlockIds(DispatchEnum):
    feedback_input = "incident-feedback-notification-feedback-input"
    rating_select = "incident-feedback-notification-rating-select"
    anonymous_checkbox = "incident-feedback-notification-anonymous-checkbox"


class CaseFeedbackNotificationBlockIds(DispatchEnum):
    feedback_input = "case-feedback-notification-feedback-input"
    rating_select = "case-feedback-notification-rating-select"
    anonymous_checkbox = "case-feedback-notification-anonymous-checkbox"


class IncidentFeedbackNotificationActionIds(DispatchEnum):
    feedback_input = "incident-feedback-notification-feedback-input"
    rating_select = "incident-feedback-notification-rating-select"
    anonymous_checkbox = "incident-feedback-notification-anonymous-checkbox"


class CaseFeedbackNotificationActionIds(DispatchEnum):
    feedback_input = "case-feedback-notification-feedback-input"
    rating_select = "case-feedback-notification-rating-select"
    anonymous_checkbox = "case-feedback-notification-anonymous-checkbox"


class IncidentFeedbackNotificationActions(DispatchEnum):
    submit = "incident-feedback-notification-submit"
    provide = ConversationButtonActions.feedback_notification_provide


class CaseFeedbackNotificationActions(DispatchEnum):
    submit = "case-feedback-notification-submit"
    provide = ConversationButtonActions.case_feedback_notification_provide


class ServiceFeedbackNotificationBlockIds(DispatchEnum):
    anonymous_checkbox = "service-feedback-notification-anonymous-checkbox"
    feedback_input = "service-feedback-notification-feedback-input"
    hours_input = "service-feedback-notification-hours-input"
    rating_select = "service-feedback-notification-rating-select"


class ServiceFeedbackNotificationActionIds(DispatchEnum):
    anonymous_checkbox = "service-feedback-notification-anonymous-checkbox"
    feedback_input = "service-feedback-notification-feedback-input"
    hours_input = "service-feedback-notification-hours-input"
    rating_select = "service-feedback-notification-rating-select"


class ServiceFeedbackNotificationActions(DispatchEnum):
    provide = ConversationButtonActions.service_feedback
    submit = "service-feedback-notification-submit"
