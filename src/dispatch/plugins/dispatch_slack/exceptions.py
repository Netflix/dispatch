from dispatch.exceptions import DispatchException


class BotNotPresentError(DispatchException):
    code = "bot_not_present"
    msg_template = "{msg}"


class CommandError(DispatchException):
    code = "command"
    msg_template = "{msg}"


class ContextError(DispatchException):
    code = "context"
    msg_template = "{msg}"


class EventError(DispatchException):
    code = "command"
    msg_template = "{msg}"


class RoleError(DispatchException):
    code = "role"
    msg_template = "{msg}"


class SubmissionError(DispatchException):
    code = "submission"
    msg_template = "{msg}"
