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
from dispatch.incident.models import Incident
from dispatch.individual.models import IndividualContact, IndividualContactRead
from dispatch.document.models import Document, DocumentRead
from dispatch.team.models import TeamContact, TeamContactRead
from dispatch.service.models import Service, ServiceRead
from dispatch.individual import service as individual_service
from dispatch.plugins import dispatch_core as dispatch_plugin
from dispatch.incident import service as incident_service
from dispatch.team import service as team_service
from dispatch.plugin import service as plugin_service
from dispatch.route import service as route_service
from dispatch.service import service as service_service

from dispatch.plugins.bases import (
    ParticipantPlugin,
    DocumentResolverPlugin,
    AuthenticationProviderPlugin,
    TicketPlugin,
    ContactPlugin,
)


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
                jwt_opts = {"verify_at_hash": False}
            # If DISPATCH_JWT_AUDIENCE is defined, the we must include audience in the decode
            if DISPATCH_JWT_AUDIENCE:
                data = jwt.decode(token, key, audience=DISPATCH_JWT_AUDIENCE, options=jwt_opts)
            else:
                data = jwt.decode(token, key, options=jwt_opts)
        except JWTError as err:
            log.debug("JWT Decode error: {}".format(err))
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
        db_session=None,
    ):
        """Creates a Dispatch ticket."""
        incident = incident_service.get(db_session=db_session, incident_id=incident_id)

        resource_id = (
            f"dispatch-{incident.project.organization.slug}-{incident.project.slug}-{incident.id}"
        )
        return {
            "resource_id": resource_id,
            "weblink": f"{DISPATCH_UI_URL}/{incident.project.organization.name}/incidents/{resource_id}?project={incident.project.name}",
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
        self,
        incident: Incident,
        db_session=None,
    ):
        """Fetches documents from Dispatch."""
        recommendation = route_service.get(
            db_session=db_session, incident=incident, models=[(Document, DocumentRead)]
        )
        return recommendation.matches


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
        incident: Incident,
        db_session=None,
    ):
        """Fetches participants from Dispatch."""
        models = [
            (IndividualContact, IndividualContactRead),
            (Service, ServiceRead),
            (TeamContact, TeamContactRead),
        ]
        recommendation = route_service.get(db_session=db_session, incident=incident, models=models)

        log.debug(f"Recommendation: {recommendation}")

        individual_contacts = []
        team_contacts = []
        for match in recommendation.matches:
            if match.resource_type == TeamContact.__name__:
                team = team_service.get_or_create(
                    db_session=db_session, email=match.resource_state["email"], incident=incident
                )
                team_contacts.append(team)

            if match.resource_type == IndividualContact.__name__:
                individual = individual_service.get_or_create(
                    db_session=db_session, email=match.resource_state["email"], incident=incident
                )

                individual_contacts.append((individual, None))

            # we need to do more work when we have a service
            if match.resource_type == Service.__name__:
                plugin_instance = plugin_service.get_active_instance_by_slug(
                    db_session=db_session,
                    slug=match.resource_state["type"],
                    project_id=incident.project.id,
                )

                if plugin_instance:
                    if plugin_instance.enabled:
                        log.debug(
                            f"Resolving service contact. ServiceContact: {match.resource_state}"
                        )
                        # ensure that service is enabled
                        service = service_service.get_by_external_id_and_project_id(
                            db_session=db_session,
                            external_id=match.resource_state["external_id"],
                            project_id=incident.project_id,
                        )
                        if service.is_active:
                            individual_email = plugin_instance.instance.get(
                                match.resource_state["external_id"]
                            )

                            individual = individual_service.get_or_create(
                                db_session=db_session, email=individual_email, incident=incident
                            )

                            individual_contacts.append((individual, match.resource_state["id"]))
                    else:
                        log.warning(
                            f"Skipping service contact. Service: {match.resource_state['name']} Reason: Associated service plugin not enabled."
                        )
                else:
                    log.warning(
                        f"Skipping service contact. Service: {match.resource_state['name']} Reason: Associated service plugin not found."
                    )

        db_session.commit()
        return individual_contacts, team_contacts
