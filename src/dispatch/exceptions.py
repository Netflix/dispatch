class DispatchException(Exception):
    pass


class InvalidConfiguration(DispatchException):
    pass


class InvalidFilterPolicy(DispatchException):
    pass


class DispatchPluginException(DispatchException):
    pass
