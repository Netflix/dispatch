from dispatch.conversation.enums import ConversationButtonActions
from dispatch.enums import DispatchEnum


class FeedbackNotificationBlockIds(DispatchEnum):
    feedback_input = "feedback-notification-feedback-input"
    rating_select = "feedback-notification-rating-select"
    anonymous_checkbox = "feedback-notification-anonymous-checkbox"


class FeedbackNotificationActionIds(DispatchEnum):
    feedback_input = "feedback-notification-feedback-input"
    rating_select = "feedback-notification-rating-select"
    anonymous_checkbox = "feedback-notification-anonymous-checkbox"


class FeedbackNotificationActions(DispatchEnum):
    submit = "feedback-notification-submit"
    provide = ConversationButtonActions.feedback_notification_provide
