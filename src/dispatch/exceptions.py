from pydantic.errors import PydanticValueError


class DispatchException(Exception):
    pass


class DispatchPluginException(DispatchException):
    pass


class NotFoundError(PydanticValueError):
    code = "not_found"
    msg_template = ""


class FieldNotFoundError(PydanticValueError):
    code = "not_found.field"
    msg_template = ""


class ModelNotFoundError(PydanticValueError):
    code = "not_found.model"
    msg_template = ""


class ExistsError(PydanticValueError):
    code = "exists"
    msg_template = ""


class InvalidConfigurationError(PydanticValueError):
    code = "invalid.configuration"
    msg_template = ""


class InvalidFilterError(PydanticValueError):
    code = "invalid.filter"
    msg_template = ""


class InvalidValueError(PydanticValueError):
    code = "invalid"
    msg_template = ""
