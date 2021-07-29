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


class ExistsError(PydanticValueError):
    code = "exists"


class InvalidConfigurationError(PydanticValueError):
    code = "invalid.configuration"


class InvalidValueError(PydanticValueError):
    code = "invalid"
