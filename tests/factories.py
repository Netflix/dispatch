import uuid

from pytz import UTC
from datetime import datetime

from factory import Sequence, post_generation, SubFactory, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText, FuzzyDateTime

from dispatch.database import SessionLocal

from dispatch.conference.models import Conference
from dispatch.conversation.models import Conversation
from dispatch.definition.models import Definition
from dispatch.document.models import Document
from dispatch.event.models import Event
from dispatch.group.models import Group
from dispatch.incident.models import Incident
from dispatch.incident_priority.models import IncidentPriority
from dispatch.incident_type.models import IncidentType
from dispatch.individual.models import IndividualContact
from dispatch.participant.models import Participant
from dispatch.participant_role.models import ParticipantRole
from dispatch.policy.models import Policy
from dispatch.route.models import Recommendation, RecommendationAccuracy
from dispatch.service.models import Service
from dispatch.report.models import Report
from dispatch.storage.models import Storage
from dispatch.tag.models import Tag
from dispatch.task.models import Task
from dispatch.team.models import TeamContact
from dispatch.term.models import Term
from dispatch.ticket.models import Ticket


class BaseFactory(SQLAlchemyModelFactory):
    """Base Factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"


class TimeStampBaseFactory(BaseFactory):
    """Timestamp Base Factory."""

    created_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    updated_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))


class ResourceBaseFactory(TimeStampBaseFactory):
    """Resource Base Factory."""

    resource_type = FuzzyChoice(["one", "two", "three"])
    resource_id = FuzzyText()
    weblink = FuzzyText()

    @post_generation
    def incident_priorities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for priority in extracted:
                self.incident_priorities.append(priority)

    @post_generation
    def incident_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident_type in extracted:
                self.incident_types.append(incident_type)

    @post_generation
    def terms(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for term in extracted:
                self.terms.append(term)


class ContactBaseFactory(TimeStampBaseFactory):
    """Contact Base Factory."""

    is_active = True
    is_external = False
    contact_type = FuzzyChoice(["one", "two"])
    email = Sequence(lambda n: f"user{n}@example.com")
    company = FuzzyText()
    notes = FuzzyText()
    owner = "kevin@example.com"

    @post_generation
    def incident_priorities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for priority in extracted:
                self.incident_priorities.append(priority)

    @post_generation
    def incident_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident_type in extracted:
                self.incident_types.append(incident_type)

    @post_generation
    def terms(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for term in extracted:
                self.terms.append(term)


class TagFactory(BaseFactory):
    """Tag Factory."""

    name = Sequence(lambda n: f"app{n}")
    uri = "https://example.com"
    uri_source = "foobar"

    class Meta:
        """Factory Configuration."""

        model = Tag

    @post_generation
    def incidents(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident in extracted:
                self.incidents.append(incident)


class ConversationFactory(ResourceBaseFactory):
    """Conversation Factory."""

    channel_id = Sequence(lambda n: f"channel{n}")

    class Meta:
        """Factory Configuration."""

        model = Conversation


class DefinitionFactory(BaseFactory):
    """Definition Factory."""

    text = FuzzyText()
    source = "dispatch"

    class Meta:
        """Factory Configuration."""

        model = Definition

    @post_generation
    def terms(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for term in extracted:
                self.terms.append(term)

    @post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for team in extracted:
                self.teams.append(team)


class DocumentFactory(ResourceBaseFactory):
    """Document Factory."""

    name = Sequence(lambda n: f"document{n}")
    description = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Document


class GroupFactory(ResourceBaseFactory):
    """Group Factory."""

    name = Sequence(lambda n: f"group{n}")
    email = Sequence(lambda n: f"group{n}@example.com")

    class Meta:
        """Factory Configuration."""

        model = Group


class IncidentPriorityFactory(BaseFactory):
    """Incident Priority Factory."""

    name = FuzzyText()
    description = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = IncidentPriority


class IncidentTypeFactory(BaseFactory):
    """Incident Type Factory."""

    name = FuzzyText()
    description = FuzzyText()
    slug = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = IncidentType


class IndividualContactFactory(ContactBaseFactory):
    """Individual Contact Factory."""

    name = Sequence(lambda n: f"Joe{n}")
    mobile_phone = "111-111-1111"
    office_phone = "111-111-1111"
    title = FuzzyText()
    weblink = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = IndividualContact


class ParticipantRoleFactory(BaseFactory):
    """Participant Factory."""

    assumed_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    renounced_at = None
    role = FuzzyChoice(["Incident Commander", "Reporter", "Scribe", "Liaison"])

    class Meta:
        """Factory Configuration."""

        model = ParticipantRole

    @post_generation
    def participant(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.participant_id = extracted.id


class ParticipantFactory(BaseFactory):
    """Participant Factory."""

    is_active = True
    active_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    inactive_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))

    class Meta:
        """Factory Configuration."""

        model = Participant

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id

    @post_generation
    def individual_contact(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.individual_contact_id = extracted.id

    @post_generation
    def team(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.team_id = extracted.id

    @post_generation
    def participant_roles(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for participant_role in extracted:
                self.participant_roles.append(participant_role)

    @post_generation
    def status_reports(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for report in extracted:
                self.status_reports.append(report)


class PolicyFactory(BaseFactory):
    """Policy Factory."""

    name = Sequence(lambda n: f"policy{n}")
    description = FuzzyText()
    expression = ""

    class Meta:
        """Factory Configuration."""

        model = Policy


class RecommendationAccuracyFactory(BaseFactory):
    """Recommendation Accuracy Factory."""

    correct = True
    resource_type = ""

    class Meta:
        """Factory Configuration."""

        model = RecommendationAccuracy

    @post_generation
    def recommendation(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.recommended_id = extracted.id


class RecommendationFactory(BaseFactory):
    """Recommendation Factory."""

    text = FuzzyText()
    accuracy = SubFactory(RecommendationAccuracy)

    class Meta:
        """Factory Configuration."""

        model = Recommendation

    @post_generation
    def incident_priorities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for priority in extracted:
                self.incident_priorities.append(priority)

    @post_generation
    def incident_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident_type in extracted:
                self.incident_types.append(incident_type)

    @post_generation
    def matched_terms(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for term in extracted:
                self.matched_terms.append(term)

    @post_generation
    def documents(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for document in extracted:
                self.documents.append(document)

    @post_generation
    def team_contacts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for team_contact in extracted:
                self.team_contacts.append(team_contact)

    @post_generation
    def service_contacts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for service_contact in extracted:
                self.service_contacts.append(service_contact)

    @post_generation
    def individual_contacts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for individual_contact in extracted:
                self.individual_contacts.append(individual_contact)


class ServiceFactory(TimeStampBaseFactory):
    """Service Factory."""

    is_active = True
    name = Sequence(lambda n: f"service{n}")
    external_id = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Service

    @post_generation
    def incidents(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident in extracted:
                self.incidents.append(incident)

    @post_generation
    def incident_priorities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for priority in extracted:
                self.incident_priorities.append(priority)

    @post_generation
    def incident_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident_type in extracted:
                self.incident_types.append(incident_type)

    @post_generation
    def terms(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for term in extracted:
                self.terms.append(term)


class ReportFactory(BaseFactory):
    """Report Factory."""

    created_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    details = FuzzyText()
    details_raw = FuzzyText()
    type = FuzzyChoice(["Tactical Report", "Executive Report"])

    class Meta:
        """Factory Configuration."""

        model = Report

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id

    @post_generation
    def participant(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.participant_id = extracted.id


class StorageFactory(ResourceBaseFactory):
    """Storage Factory."""

    class Meta:
        """Factory Configuration"""

        model = Storage


class TaskFactory(ResourceBaseFactory):
    """Task Factory."""

    resolved_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    last_reminder_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    creator = "joe@example.com"
    assignees = "joe@example.com"
    description = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Task

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id


class TeamContactFactory(ContactBaseFactory):
    """Team Contact Factory."""

    name = Sequence(lambda n: f"team{n}")
    notes = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = TeamContact

    @post_generation
    def incidents(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident in extracted:
                self.incidents.append(incident)

    @post_generation
    def incident_priorities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for priority in extracted:
                self.incident_priorities.append(priority)

    @post_generation
    def incident_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for incident_type in extracted:
                self.incident_types.append(incident_type)

    @post_generation
    def terms(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for term in extracted:
                self.terms.append(term)


class TermFactory(BaseFactory):
    """Term Factory."""

    text = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Term


class TicketFactory(ResourceBaseFactory):
    """Ticket Factory."""

    resource_id = FuzzyText()
    resource_type = FuzzyText()
    weblink = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Ticket


class IncidentFactory(BaseFactory):
    """Incident Factory."""

    id = Sequence(lambda n: f"1{n}")
    title = FuzzyText()
    description = FuzzyText()
    status = FuzzyChoice(["Active", "Stable", "Closed"])

    class Meta:
        """Factory Configuration."""

        model = Incident

    @post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for participant in extracted:
                self.participants.append(participant)


class EventFactory(BaseFactory):
    """Event Factory."""

    uuid = LazyAttribute(lambda _: str(uuid.uuid4()))
    started_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    ended_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    source = FuzzyText()
    description = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Event

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id

    @post_generation
    def individual_contact(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.individual_contact_id = extracted.id


class ConferenceFactory(ResourceBaseFactory):
    """Conference Factory."""

    class Meta:
        model = Conference

    conference_id = Sequence(lambda n: f"conference{n}")
    conference_challenge = FuzzyText()
    incident = SubFactory(IncidentFactory)
