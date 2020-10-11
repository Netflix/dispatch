"""
.. module: dispatch.plugins.dispatch_core.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import base64
import json
import logging

import requests
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param

from jose import JWTError, jwt
from jose.exceptions import JWKError
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request

from dispatch.config import DISPATCH_UI_URL
from dispatch.incident_priority.models import IncidentPriority
from dispatch.incident_type.models import IncidentType
from dispatch.individual import service as individual_service
from dispatch.plugins import dispatch_core as dispatch_plugin
from dispatch.plugin import service as plugin_service
from dispatch.plugins.bases import (
    ParticipantPlugin,
    DocumentResolverPlugin,
    AuthenticationProviderPlugin,
    TicketPlugin,
    ContactPlugin,
)

from dispatch.route import service as route_service
from dispatch.route.models import RouteRequest

from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS,
    DISPATCH_PKCE_DONT_VERIFY_AT_HASH,
    DISPATCH_JWT_SECRET,
    DISPATCH_JWT_AUDIENCE,
    DISPATCH_JWT_EMAIL_OVERRIDE,
)

log = logging.getLogger(__name__)


class BasicAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Dispatch Plugin - Basic Authentication Provider"
    slug = "dispatch-auth-provider-basic"
    description = "Generic basic authentication provider."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def get_current_user(self, request: Request, **kwargs):
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            log.exception(
                f"Malformed authorization header. Scheme: {scheme} Param: {param} Authorization: {authorization}"
            )
            return

        token = authorization.split()[1]

        try:
            data = jwt.decode(token, DISPATCH_JWT_SECRET)
        except (JWKError, JWTError) as e:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=str(e))
        return data["email"]


class PKCEAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Dispatch Plugin - PKCE Authentication Provider"
    slug = "dispatch-auth-provider-pkce"
    description = "Generic PCKE authentication provider."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def get_current_user(self, request: Request, **kwargs):
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )

        authorization: str = request.headers.get(
            "Authorization", request.headers.get("authorization")
        )
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise credentials_exception

        token = authorization.split()[1]

        # Parse out the Key information. Add padding just in case
        key_info = json.loads(base64.b64decode(token.split(".")[0] + "=========").decode("utf-8"))

        # Grab all possible keys to account for key rotation and find the right key
        keys = requests.get(DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS).json()["keys"]
        for potential_key in keys:
            if potential_key["kid"] == key_info["kid"]:
                key = potential_key

        try:
            jwt_opts = {}
            if DISPATCH_PKCE_DONT_VERIFY_AT_HASH:
                jwt_opts = {'verify_at_hash': False}
            # If DISPATCH_JWT_AUDIENCE is defined, the we must include audience in the decode
            if DISPATCH_JWT_AUDIENCE:
                data = jwt.decode(token, key, audience=DISPATCH_JWT_AUDIENCE, options=jwt_opts)
            else:
                data = jwt.decode(token, key, options=jwt_opts)
        except JWTError as err:
            log.debug('JWT Decode error: {}'.format(err))
            raise credentials_exception

        # Support overriding where email is returned in the id token
        if DISPATCH_JWT_EMAIL_OVERRIDE:
            return data[DISPATCH_JWT_EMAIL_OVERRIDE]
        else:
            return data["email"]


class DispatchTicketPlugin(TicketPlugin):
    title = "Dispatch Plugin - Ticket Management"
    slug = "dispatch-ticket"
    description = "Uses dispatch itself to create a ticket."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def create(
        self,
        incident_id: int,
        title: str,
        incident_type: str,
        incident_priority: str,
        commander: str,
        reporter: str,
        plugin_metadata: dict,
    ):
        """Creates a Dispatch ticket."""
        resource_id = f"dispatch-{incident_id}"
        return {
            "resource_id": resource_id,
            "weblink": f"{DISPATCH_UI_URL}/incidents/{resource_id}",
            "resource_type": "dispatch-internal-ticket",
        }

    def update(
        self,
        ticket_id: str,
        title: str,
        description: str,
        incident_type: str,
        priority: str,
        status: str,
        commander_email: str,
        reporter_email: str,
        conversation_weblink: str,
        conference_weblink: str,
        document_weblink: str,
        storage_weblink: str,
        cost: float,
        incident_type_plugin_metadata: dict = {},
    ):
        """Updates the incident."""
        return


class DispatchDocumentResolverPlugin(DocumentResolverPlugin):
    title = "Dispatch Plugin - Document Resolver"
    slug = "dispatch-document-resolver"
    description = "Uses dispatch itself to resolve incident documents."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def get(
        self, incident_type: str, incident_priority: str, incident_description: str, db_session=None
    ):
        """Fetches documents from Dispatch."""
        route_in = {
            "text": incident_description,
            "context": {
                "incident_priorities": [incident_priority],
                "incident_types": [incident_type],
                "terms": [],
            },
        }

        route_in = RouteRequest(**route_in)
        recommendation = route_service.get(db_session=db_session, route_in=route_in)
        return recommendation.documents


class DispatchContactPlugin(ContactPlugin):
    title = "Dispatch Plugin - Contact plugin"
    slug = "dispatch-contact"
    description = "Uses dispatch itself to resolve incident participants."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def get(self, email, db_session=None):
        return getattr(
            individual_service.get_by_email(db_session=db_session, email=email),
            "__dict__",
            {"email": email, "fullname": email},
        )


class DispatchParticipantResolverPlugin(ParticipantPlugin):
    title = "Dispatch Plugin - Participant Resolver"
    slug = "dispatch-participant-resolver"
    description = "Uses dispatch itself to resolve incident participants."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def get(
        self,
        incident_type: IncidentType,
        incident_priority: IncidentPriority,
        incident_description: str,
        db_session=None,
    ):
        """Fetches participants from Dispatch."""
        route_in = {
            "text": incident_description,
            "context": {
                "incident_priorities": [incident_priority],
                "incident_types": [incident_type],
                "terms": [],
            },
        }

        route_in = RouteRequest(**route_in)
        recommendation = route_service.get(db_session=db_session, route_in=route_in)

        log.debug(f"Recommendation: {recommendation}")
        # we need to resolve our service contacts to individuals
        for s in recommendation.service_contacts:
            plugin = plugin_service.get_by_slug(db_session=db_session, slug=s.type)

            if plugin:
                if plugin.enabled:
                    log.debug(f"Resolving service contact. ServiceContact: {s}")
                    individual_email = plugin.instance.get(s.external_id)

                    individual = individual_service.get_or_create(
                        db_session=db_session, email=individual_email
                    )
                    recommendation.individual_contacts.append(individual)
                else:
                    log.warning(
                        f"Skipping service contact. Service: {s.name} Reason: Associated service plugin not enabled."
                    )
            else:
                log.warning(
                    f"Skipping service contact. Service: {s.name} Reason: Associated service plugin not found."
                )

        db_session.commit()
        return list(recommendation.individual_contacts), list(recommendation.team_contacts)
