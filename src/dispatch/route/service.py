import logging
from typing import Any, Dict, List

from sqlalchemy import func

from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_priority.models import IncidentPriority
from dispatch.incident_type import service as incident_type_service
from dispatch.incident_type.models import IncidentType
from dispatch.term.models import Term

from .models import Recommendation, RecommendationAccuracy, RouteRequest, ContextBase

log = logging.getLogger(__name__)


def get_terms(db_session, text: str) -> List[str]:
    """Get terms from request."""
    all_terms = db_session.query(Term).all()
    phrases = build_term_vocab([t.text for t in all_terms])
    matcher = build_phrase_matcher("dispatch-terms", phrases)
    extracted_terms = extract_terms_from_text(text, matcher)
    return extracted_terms


# TODO is there a better way to deduplicate across sqlalchemy models?
def deduplicate_resources(resources: List[dict]) -> Dict:
    """Creates a new dict adding new resources if they are not yet seen."""
    contact_set = {}
    for c in resources:
        key = f"{type(c).__name__}-{c.id}"
        if key not in contact_set.keys():
            contact_set[key] = c

    return list(contact_set.values())


def resource_union(resources: List[dict], inputs: int) -> Dict:
    """Ensures the an item occurs in the resources list at least n times."""
    resource_set = {}
    for c in resources:
        key = f"{type(c).__name__}-{c.id}"
        if key not in resource_set.keys():
            resource_set[key] = (1, c)
        else:
            count, obj = resource_set[key]
            resource_set[key] = (count + 1, obj)

    unions = []
    for key, value in resource_set.items():
        count, obj = value
        if count >= inputs:
            unions.append(obj)
    return unions


def get_resources_from_incident_types(db_session, incident_types: List[str]) -> list:
    """Get all resources related to a specific incident type."""
    incident_types = [i.name for i in incident_types]
    incident_type_models = (
        db_session.query(IncidentType).filter(IncidentType.name.in_(incident_types)).all()
    )

    resources = []
    for i in incident_type_models:
        resources += i.teams
        resources += i.individuals
        resources += i.services
        resources += i.documents

    return resources


def get_resources_from_priorities(db_session, incident_priorities: List[str]) -> list:
    """Get all resources related to a specific priority."""
    incident_priorities = [i.name for i in incident_priorities]
    incident_priority_models = (
        db_session.query(IncidentPriority)
        .filter(IncidentPriority.name.in_(incident_priorities))
        .all()
    )

    resources = []
    for i in incident_priority_models:
        resources += i.teams
        resources += i.individuals
        resources += i.services
        resources += i.documents

    return resources


def get_resources_from_context(db_session, context: ContextBase):
    """Fetch relevent resources based on context only."""
    resources = []
    if context.incident_types:
        resources += get_resources_from_incident_types(
            db_session, incident_types=context.incident_types
        )

    if context.incident_priorities:
        resources += get_resources_from_priorities(
            db_session, incident_priorities=context.incident_priorities
        )

    inputs = 0
    if context.incident_priorities:
        inputs += 1

    if context.incident_types:
        inputs += 1

    resources = resource_union(resources, inputs)

    if context.terms:
        _, term_resources = get_resources_from_terms(db_session, terms=context.terms)
        resources += term_resources

    return resources


def get_resources_from_terms(db_session, terms: List[str]):
    """Fetch resources based solely on connected terms with the text."""
    # lookup extracted terms
    matched_terms = (
        db_session.query(Term)
        .filter(func.upper(Term.text).in_([func.upper(t) for t in terms]))
        .all()
    )

    # find resources associated with those terms
    resources = []
    for t in matched_terms:
        resources += t.teams
        resources += t.individuals
        resources += t.services
        resources += t.documents

    return matched_terms, resources


# TODO contacts could be List[Union(...)]
def create_recommendation(
    *, db_session, text=str, context: ContextBase, matched_terms: List[Term], resources: List[Any]
):
    """Create recommendation object for accuracy tracking."""
    accuracy = [
        RecommendationAccuracy(resource_id=r.id, resource_type=type(r).__name__) for r in resources
    ]

    incident_priorities = [
        incident_priority_service.get_by_name(db_session=db_session, name=n.name)
        for n in context.incident_priorities
    ]
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, name=n.name)
        for n in context.incident_types
    ]

    service_contacts = [x for x in resources if type(x).__name__ == "Service"]
    individual_contacts = [x for x in resources if type(x).__name__ == "IndividualContact"]
    team_contacts = [x for x in resources if type(x).__name__ == "TeamContact"]
    documents = [x for x in resources if type(x).__name__ == "Document"]

    log.debug(
        f"Recommendation: Documents: {documents} Individuals: {individual_contacts} Teams: {team_contacts} Services: {service_contacts}"
    )

    r = Recommendation(
        accuracy=accuracy,
        service_contacts=service_contacts,
        individual_contacts=individual_contacts,
        team_contacts=team_contacts,
        documents=documents,
        incident_types=incident_types,
        incident_priorities=incident_priorities,
        matched_terms=matched_terms,
        text=text,
    )

    db_session.add(r)
    db_session.commit()
    return r


def get(*, db_session, route_in: RouteRequest) -> Dict[Any, Any]:
    """Get routed resources."""
    resources = []
    matched_terms = []

    if route_in.context:
        resources.extend(
            get_resources_from_context(db_session=db_session, context=route_in.context)
        )
    if route_in.text:
        # get terms from text (question, incident description, etc,.)
        text_terms = get_terms(db_session, text=route_in.text)
        resource_matched_terms, term_resources = get_resources_from_terms(
            db_session=db_session, terms=text_terms
        )
        route_in.context.terms.extend(resource_matched_terms)
        resources.extend(term_resources)

    resources = deduplicate_resources(resources)

    # create a recommandation entry we can use to data mine at a later time
    recommendation = create_recommendation(
        db_session=db_session,
        text=route_in.text,
        context=route_in.context,
        resources=resources,
        matched_terms=matched_terms,
    )

    return recommendation
