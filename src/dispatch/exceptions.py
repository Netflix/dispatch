from pydantic.errors import PydanticValueError


class DispatchException(Exception):
    pass


class InvalidConfiguration(DispatchException):
    pass


class InvalidFilterPolicy(DispatchException):
    pass


class DispatchPluginException(DispatchException):
    pass


class NotFoundError(PydanticValueError):
    code = "not_found"
    msg_template = ""


class ExistsError(PydanticValueError):
    code = "exists"
    msg_template = ""


class InvalidConfigurationError(PydanticValueError):
    code = "invalid.configuration"
    msg_template = ""


class InvalidValueError(PydanticValueError):
    code = "invalid"
    msg_template = ""
