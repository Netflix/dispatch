"""
.. module: dispatch.plugins.dispatch_core.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

import requests
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param

from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request

from dispatch.individual import service as individual_service
from dispatch.plugins import dispatch_core as dispatch_plugin
from dispatch.plugins.base import plugins
from dispatch.plugins.bases import (
    ParticipantPlugin,
    DocumentResolverPlugin,
    AuthenticationProviderPlugin,
)

from dispatch.route import service as route_service
from dispatch.route.models import RouteRequest

from dispatch.config import DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS

log = logging.getLogger(__name__)


class PKCEAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Dispatch - PKCE Authentication Provider"
    slug = "dispatch-auth-provider-pkce"
    description = "Generic PCKE authentication provider."
    version = dispatch_plugin.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/netflix/dispatch.git"

    def get_current_user(self, request: Request, **kwargs):
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )

        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise credentials_exception

        token = authorization.split()[1]
        key = requests.get(DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS).json()["keys"][0]

        try:
            data = jwt.decode(token, key)
        except JWTError:
            raise credentials_exception

        return data["email"]


class DispatchDocumentResolverPlugin(DocumentResolverPlugin):
    title = "Dispatch - Document Resolver"
    slug = "dispatch-document-resolver"
    description = "Uses dispatch itself to resolve incident documents."
    version = dispatch_plugin.__version__

    author = "Kevin Glisson"
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


class DispatchParticipantPlugin(ParticipantPlugin):
    title = "Dispatch - Participants"
    slug = "dispatch-participants"
    description = "Uses dispatch itself to determine participants."
    version = dispatch_plugin.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/netflix/dispatch.git"

    def get(
        self,
        incident_type: str,
        incident_priority: str,
        incident_description: str,
        db_session=None,
    ):
        """Fetches participants from Dispatch."""
        route_in = {
            "text": incident_description,
            "context": {
                "incident_priorities": [incident_priority.__dict__],
                "incident_types": [incident_type.__dict__],
                "terms": [],
            },
        }

        route_in = RouteRequest(**route_in)
        recommendation = route_service.get(db_session=db_session, route_in=route_in)

        log.debug(f"Recommendation: {recommendation}")
        # we need to resolve our service contacts to individuals
        for s in recommendation.service_contacts:
            p = plugins.get(s.type)
            log.debug(f"Resolving service contact. ServiceContact: {s}")
            individual_email = p.get(s.external_id)

            individual = individual_service.get_or_create(
                db_session=db_session, email=individual_email,
            )
            recommendation.individual_contacts.append(individual)

        db_session.commit()
        return list(recommendation.individual_contacts), list(recommendation.team_contacts)
