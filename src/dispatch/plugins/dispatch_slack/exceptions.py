from dispatch.exceptions import DispatchException


class CommandDispatchError(DispatchException):
    code = "command"
    msg_template = "{msg}"


class SubmissionError(DispatchException):
    code = "submission"
    msg_template = "{msg}"


class ContextError(DispatchException):
    code = "context"
    msg_template = "{msg}"


class RoleError(DispatchException):
    code = "role"
    msg_template = "{msg}"
