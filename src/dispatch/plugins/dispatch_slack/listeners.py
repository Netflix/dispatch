from logging import Logger

from typing import Optional, Callable, Sequence

from slack_bolt.kwargs_injection import build_required_kwargs
from slack_bolt.listener_matcher import ListenerMatcher
from slack_bolt.listener import Listener
from slack_bolt.middleware import Middleware
from slack_bolt.logger import get_bolt_app_logger
from slack_bolt.util.utils import get_arg_names_of_callable

from slack_bolt.response import BoltResponse
from slack_bolt.request import BoltRequest


class MultiMessageListener(Listener):
    """This listener enables multiple functions to listen to the same message."""

    app_name: str
    ack_function: Callable[..., Optional[BoltResponse]]
    lazy_functions: Sequence[Callable[..., None]]
    matchers: Sequence[ListenerMatcher]
    middleware: Sequence[Middleware]  # type: ignore
    auto_acknowledgement: bool
    arg_names: Sequence[str]
    logger: Logger

    def __init__(
        self,
        *,
        app_name: str,
        ack_function: Callable[..., Optional[BoltResponse]],
        lazy_functions: Sequence[Callable[..., None]],
        matchers: Sequence[ListenerMatcher],
        middleware: Sequence[Middleware],  # type: ignore
        auto_acknowledgement: bool = False,
        base_logger: Optional[Logger] = None,
    ):
        self.app_name = app_name
        self.ack_function = ack_function
        self.lazy_functions = lazy_functions
        self.matchers = matchers
        self.middleware = middleware
        self.auto_acknowledgement = auto_acknowledgement
        self.arg_names = get_arg_names_of_callable(ack_function)
        self.logger = get_bolt_app_logger(app_name, self.ack_function, base_logger)

    def run_ack_function(
        self,
        *,
        request: BoltRequest,
        response: BoltResponse,
    ) -> Optional[BoltResponse]:
        return self.ack_function(
            **build_required_kwargs(
                logger=self.logger,
                required_arg_names=self.arg_names,
                request=request,
                response=response,
                this_func=self.ack_function,
            )
        )
