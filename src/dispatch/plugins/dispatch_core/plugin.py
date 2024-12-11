"""
.. module: dispatch.plugins.dispatch_core.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import base64
import json
import logging
import time
from typing import Literal
from uuid import UUID

import requests
from cachetools import cached, TTLCache
from fastapi import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from jose.exceptions import JWKError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from dispatch.auth.models import DispatchUser, MfaChallenge, MfaChallengeStatus, MfaPayload
from dispatch.case import service as case_service
from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_ARN,
    DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_EMAIL_CLAIM,
    DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_PUBLIC_KEY_CACHE_SECONDS,
    DISPATCH_AUTHENTICATION_PROVIDER_HEADER_NAME,
    DISPATCH_AUTHENTICATION_PROVIDER_PKCE_JWKS,
    DISPATCH_JWT_AUDIENCE,
    DISPATCH_JWT_EMAIL_OVERRIDE,
    DISPATCH_JWT_SECRET,
    DISPATCH_PKCE_DONT_VERIFY_AT_HASH,
    DISPATCH_UI_URL,
)
from dispatch.database.core import Base
from dispatch.incident import service as incident_service
from dispatch.individual import service as individual_service
from dispatch.individual.models import IndividualContact, IndividualContactRead
from dispatch.plugin import service as plugin_service
from dispatch.plugins import dispatch_core as dispatch_plugin
from dispatch.plugins.bases import (
    AuthenticationProviderPlugin,
    ContactPlugin,
    MultiFactorAuthenticationPlugin,
    ParticipantPlugin,
    TicketPlugin,
)
from dispatch.plugins.dispatch_core.config import DispatchTicketConfiguration
from dispatch.plugins.dispatch_core.exceptions import (
    ActionMismatchError,
    ExpiredChallengeError,
    InvalidChallengeError,
    InvalidChallengeStateError,
    UserMismatchError,
)
from dispatch.plugins.dispatch_core.service import create_resource_id
from dispatch.project import service as project_service
from dispatch.route import service as route_service
from dispatch.service import service as service_service
from dispatch.service.models import Service, ServiceRead
from dispatch.team import service as team_service
from dispatch.team.models import TeamContact, TeamContactRead

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
        except (JWKError, JWTError):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=[{"msg": "Could not validate credentials"}],
            ) from None
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
            status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
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
            raise credentials_exception from err

        # Support overriding where email is returned in the id token
        if DISPATCH_JWT_EMAIL_OVERRIDE:
            return data[DISPATCH_JWT_EMAIL_OVERRIDE]
        else:
            return data["email"]


class HeaderAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Dispatch Plugin - HTTP Header Authentication Provider"
    slug = "dispatch-auth-provider-header"
    description = "Authenticate users based on HTTP request header."
    version = dispatch_plugin.__version__

    author = "Filippo Giunchedi"
    author_url = "https://github.com/filippog"

    def get_current_user(self, request: Request, **kwargs):
        value: str = request.headers.get(DISPATCH_AUTHENTICATION_PROVIDER_HEADER_NAME)
        if not value:
            log.error(
                f"Unable to authenticate. Header {DISPATCH_AUTHENTICATION_PROVIDER_HEADER_NAME} not found."
            )
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        return value


class AwsAlbAuthProviderPlugin(AuthenticationProviderPlugin):
    title = "Dispatch Plugin - AWS ALB Authentication Provider"
    slug = "dispatch-auth-provider-aws-alb"
    description = "AWS Application Load Balancer authentication provider."
    version = dispatch_plugin.__version__

    author = "ManyPets"
    author_url = "https://manypets.com/"

    @cached(cache=TTLCache(maxsize=1024, ttl=DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_PUBLIC_KEY_CACHE_SECONDS))
    def get_public_key(self, kid: str, region: str):
        log.debug("Cache miss. Requesting key from AWS endpoint.")
        url = f"https://public-keys.auth.elb.{region}.amazonaws.com/{kid}"
        req = requests.get(url)
        return req.text

    def get_current_user(self, request: Request, **kwargs):
        credentials_exception = HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
        )

        encoded_jwt: str = request.headers.get('x-amzn-oidc-data')
        if not encoded_jwt:
            log.error(
                "Unable to authenticate. Header x-amzn-oidc-data not found."
            )
            raise credentials_exception

        log.debug(f"Header x-amzn-oidc-data header received: {encoded_jwt}")

        # Validate the signer
        jwt_headers = encoded_jwt.split('.')[0]
        decoded_jwt_headers = base64.b64decode(jwt_headers)
        decoded_json = json.loads(decoded_jwt_headers)
        received_alb_arn = decoded_json['signer']

        if received_alb_arn != DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_ARN:
            log.error(
                f"Unable to authenticate. ALB ARN {received_alb_arn} does not match expected ARN {DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_ARN}"
            )
            raise credentials_exception

        # Get the key id from JWT headers (the kid field)
        kid = decoded_json['kid']

        # Get the region from the ARN
        region = DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_ARN.split(':')[3]

        # Get the public key from regional endpoint
        log.debug(f"Getting public key for kid {kid} in region {region}.")
        pub_key = self.get_public_key(kid, region)

        # Get the payload
        log.debug(f"Decoding {encoded_jwt} with public key {pub_key}.")
        payload = jwt.decode(encoded_jwt, pub_key, algorithms=['ES256'])

        return payload[DISPATCH_AUTHENTICATION_PROVIDER_AWS_ALB_EMAIL_CLAIM]


class DispatchTicketPlugin(TicketPlugin):
    title = "Dispatch Plugin - Ticket Management"
    slug = "dispatch-ticket"
    description = "Uses Dispatch itself to create a ticket."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = DispatchTicketConfiguration

    def create(
        self,
        incident_id: int,
        title: str,
        commander_email: str,
        reporter_email: str,
        plugin_metadata: dict,
        db_session=None,
    ):
        """Creates a Dispatch incident ticket."""
        incident = incident_service.get(db_session=db_session, incident_id=incident_id)

        if self.configuration and self.configuration.use_incident_name:
            resource_id = create_resource_id(f"{incident.project.slug}-{title}-{incident.id}")
        else:
            resource_id = f"dispatch-{incident.project.organization.slug}-{incident.project.slug}-{incident.id}"

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
        incident_severity: str,
        incident_priority: str,
        status: str,
        commander_email: str,
        reporter_email: str,
        conversation_weblink: str,
        document_weblink: str,
        storage_weblink: str,
        conference_weblink: str,
        dispatch_weblink: str,
        cost: float,
        incident_type_plugin_metadata: dict = None,
    ):
        """Updates a Dispatch incident ticket."""
        return

    def delete(
        self,
        ticket_id: str,
    ):
        """Deletes a Dispatch ticket."""
        return

    def create_case_ticket(
        self,
        case_id: int,
        title: str,
        assignee_email: str,
        # reporter: str,
        case_type_plugin_metadata: dict,
        db_session=None,
    ):
        """Creates a Dispatch case ticket."""
        case = case_service.get(db_session=db_session, case_id=case_id)

        resource_id = f"dispatch-{case.project.organization.slug}-{case.project.slug}-{case.id}"

        return {
            "resource_id": resource_id,
            "weblink": f"{DISPATCH_UI_URL}/{case.project.organization.name}/cases/{resource_id}?project={case.project.name}",
            "resource_type": "dispatch-internal-ticket",
        }

    def update_case_ticket(
        self,
        ticket_id: str,
        title: str,
        description: str,
        resolution: str,
        case_type: str,
        case_severity: str,
        case_priority: str,
        status: str,
        assignee_email: str,
        # reporter_email: str,
        document_weblink: str,
        storage_weblink: str,
        dispatch_weblink: str,
        case_type_plugin_metadata: dict = None,
    ):
        """Updates a Dispatch case ticket."""
        return

    def create_task_ticket(
        self,
        task_id: int,
        title: str,
        assignee_email: str,
        reporter_email: str,
        incident_ticket_key: str = None,
        task_plugin_metadata: dict = None,
        db_session=None,
    ):
        """Creates a Dispatch task ticket."""
        return {
            "resource_id": "",
            "weblink": "https://dispatch.example.com",
        }


class DispatchMfaPlugin(MultiFactorAuthenticationPlugin):
    title = "Dispatch Plugin - Multi Factor Authentication"
    slug = "dispatch-auth-mfa"
    description = "Uses dispatch itself to validate external requests."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def wait_for_challenge(
        self,
        challenge_id: UUID,
        db_session: Session,
        timeout: int = 300,
    ) -> MfaChallengeStatus:
        """Waits for a multi-factor authentication challenge."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            db_session.expire_all()
            challenge = db_session.query(MfaChallenge).filter_by(challenge_id=challenge_id).first()

            if not challenge:
                log.error(f"Challenge not found: {challenge_id}")
                raise Exception("Challenge not found.")

            if challenge.status == MfaChallengeStatus.APPROVED:
                return MfaChallengeStatus.APPROVED
            elif challenge.status == MfaChallengeStatus.DENIED:
                raise Exception("Challenge denied.")

            time.sleep(1)

        # Timeout reached
        log.warning(f"Timeout reached for challenge: {challenge_id}")

        # Update the challenge status to EXPIRED if it times out
        challenge = db_session.query(MfaChallenge).filter_by(challenge_id=challenge_id).first()
        if challenge:
            log.info(f"Updating challenge {challenge_id} status to EXPIRED")
            challenge.status = MfaChallengeStatus.EXPIRED
            db_session.commit()
        else:
            log.error(f"Challenge not found when trying to expire: {challenge_id}")

        return MfaChallengeStatus.EXPIRED

    def create_mfa_challenge(
        self,
        action: str,
        current_user: DispatchUser,
        db_session: Session,
        project_id: int,
    ) -> tuple[MfaChallenge, str]:
        """Creates a multi-factor authentication challenge."""
        project = project_service.get(db_session=db_session, project_id=project_id)

        challenge = MfaChallenge(
            action=action,
            dispatch_user_id=current_user.id,
            valid=True,
        )
        db_session.add(challenge)
        db_session.commit()

        org_slug = project.organization.slug if project.organization else "default"

        challenge_url = f"{DISPATCH_UI_URL}/{org_slug}/mfa?project_id={project_id}&challenge_id={challenge.challenge_id}&action={action}"
        return challenge, challenge_url

    def validate_mfa_token(
        self,
        payload: MfaPayload,
        current_user: DispatchUser,
        db_session: Session,
    ) -> Literal[MfaChallengeStatus.APPROVED]:
        """Validates a multi-factor authentication token."""
        challenge: MfaChallenge | None = (
            db_session.query(MfaChallenge)
            .filter_by(challenge_id=payload.challenge_id)
            .one_or_none()
        )

        if not challenge:
            raise InvalidChallengeError("Invalid challenge ID")
        if challenge.dispatch_user_id != current_user.id:
            raise UserMismatchError(
                f"Challenge does not belong to the current user: {current_user.email}"
            )
        if challenge.action != payload.action:
            raise ActionMismatchError("Action mismatch")
        if not challenge.valid:
            raise ExpiredChallengeError("Challenge is no longer valid")
        if challenge.status == MfaChallengeStatus.APPROVED:
            # Challenge has already been approved
            return challenge.status
        if challenge.status != MfaChallengeStatus.PENDING:
            raise InvalidChallengeStateError(f"Challenge is in invalid state: {challenge.status}")

        challenge.status = MfaChallengeStatus.APPROVED
        db_session.add(challenge)
        db_session.commit()

        return challenge.status

    def send_push_notification(self, items, **kwargs):
        # Implement this method if needed
        raise NotImplementedError

    def validate_mfa(self, items, **kwargs):
        # Implement this method if needed
        raise NotImplementedError


class DispatchContactPlugin(ContactPlugin):
    title = "Dispatch Plugin - Contact plugin"
    slug = "dispatch-contact"
    description = "Uses dispatch itself to fetch incident participants contact info."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def get(self, email, db_session=None):
        individual = individual_service.get_by_email_and_project(
            db_session=db_session, email=email, project_id=self.project_id
        )
        if individual is None:
            return {"email": email, "fullname": email}

        data = individual.dict()
        data["fullname"] = data["name"]
        return data


class DispatchParticipantResolverPlugin(ParticipantPlugin):
    title = "Dispatch Plugin - Participant Resolver"
    slug = "dispatch-participant-resolver"
    description = "Uses dispatch itself to resolve incident participants."
    version = dispatch_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def get(
        self,
        project_id: int,
        class_instance: Base,
        db_session=None,
    ):
        """Fetches participants from Dispatch."""
        models = [
            (IndividualContact, IndividualContactRead),
            (Service, ServiceRead),
            (TeamContact, TeamContactRead),
        ]
        recommendation = route_service.get(
            db_session=db_session,
            project_id=project_id,
            class_instance=class_instance,
            models=models,
        )

        log.debug(f"Recommendation: {recommendation}")

        individual_contacts = []
        team_contacts = []
        for match in recommendation.matches:
            if match.resource_type == TeamContact.__name__:
                team = team_service.get_or_create(
                    db_session=db_session,
                    email=match.resource_state["email"],
                    project=class_instance.project,
                )
                team_contacts.append(team)

            if match.resource_type == IndividualContact.__name__:
                individual = individual_service.get_or_create(
                    db_session=db_session,
                    email=match.resource_state["email"],
                    project=class_instance.project,
                )

                individual_contacts.append((individual, None))

            # we need to do more work when we have a service
            if match.resource_type == Service.__name__:
                plugin_instance = plugin_service.get_active_instance_by_slug(
                    db_session=db_session,
                    slug=match.resource_state["type"],
                    project_id=project_id,
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
                            project_id=project_id,
                        )
                        if service.is_active:
                            individual_email = plugin_instance.instance.get(
                                match.resource_state["external_id"]
                            )

                            individual = individual_service.get_or_create(
                                db_session=db_session,
                                email=individual_email,
                                project=class_instance.project,
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
