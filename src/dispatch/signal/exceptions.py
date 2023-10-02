from dispatch.exceptions import DispatchException


class SignalNotIdentifiedException(DispatchException):
    pass


class SignalNotDefinedException(DispatchException):
    pass


class SignalNotEnabledException(DispatchException):
    pass
