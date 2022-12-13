from dispatch.exceptions import DispatchException


class ContextError(DispatchException):
    code = "context"
    msg_template = "{msg}"


class RoleError(DispatchException):
    code = "role"
    msg_template = "{msg}"
