import logging

from starlette.config import Config


log = logging.getLogger(__name__)


config = Config(".env")


DISPATCH_JWT_AUDIENCE = config("DISPATCH_JWT_AUDIENCE", default=None)
DISPATCH_JWT_EMAIL_OVERRIDE = config("DISPATCH_JWT_EMAIL_OVERRIDE", default=None)


if config.get("DISPATCH_AUTHENTICATION_PROVIDER_SLUG") == "dispatch-auth-provider-pkce":
    if not DISPATCH_JWT_AUDIENCE:
        log.warn("No JWT Audience specified. This is required for IdPs like Okta")
    if not DISPATCH_JWT_EMAIL_OVERRIDE:
        log.warn("No JWT Email Override specified. 'email' is expected in the idtoken.")
