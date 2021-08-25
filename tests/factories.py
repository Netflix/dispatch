import uuid

from pytz import UTC
from datetime import datetime

from faker import Faker

from factory import Sequence, post_generation, SubFactory, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText, FuzzyDateTime, FuzzyInteger

from dispatch.database.core import SessionLocal

from dispatch.auth.models import DispatchUser  # noqa
from dispatch.conference.models import Conference
from dispatch.conversation.models import Conversation
from dispatch.definition.models import Definition
from dispatch.document.models import Document
from dispatch.event.models import Event
from dispatch.feedback.models import Feedback
from dispatch.group.models import Group
from dispatch.incident.models import Incident
from dispatch.incident_cost.models import IncidentCost
from dispatch.incident_cost_type.models import IncidentCostType
from dispatch.incident_priority.models import IncidentPriority
from dispatch.incident_role.models import IncidentRole
from dispatch.incident_type.models import IncidentType
from dispatch.individual.models import IndividualContact
from dispatch.notification.models import Notification
from dispatch.organization.models import Organization
from dispatch.participant.models import Participant
from dispatch.participant_role.models import ParticipantRole
from dispatch.plugin.models import Plugin, PluginInstance
from dispatch.project.models import Project
from dispatch.report.models import Report
from dispatch.route.models import Recommendation, RecommendationMatch
from dispatch.search_filter.models import SearchFilter
from dispatch.service.models import Service
from dispatch.storage.models import Storage
from dispatch.tag.models import Tag
from dispatch.tag_type.models import TagType
from dispatch.task.models import Task
from dispatch.team.models import TeamContact
from dispatch.term.models import Term
from dispatch.ticket.models import Ticket
from dispatch.workflow.models import Workflow, WorkflowInstance


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


class OrganizationFactory(BaseFactory):
    """Organization Factory."""

    name = Sequence(lambda n: f"organization{n}")
    description = FuzzyText()
    default = Faker().pybool()
    banner_enabled = Faker().pybool()
    banner_color = Faker().color()
    banner_text = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Organization

    @post_generation
    def projects(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for project in extracted:
                self.projects.append(project)


class ProjectFactory(BaseFactory):
    """Project Factory."""

    name = Sequence(lambda n: f"project{n}")
    description = FuzzyText()
    default = Faker().pybool()
    color = Faker().color()

    class Meta:
        """Factory Configuration."""

        model = Project

    @post_generation
    def organization(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.organization_id = extracted.id


class ResourceBaseFactory(TimeStampBaseFactory):
    """Resource Base Factory."""

    resource_type = FuzzyChoice(["one", "two", "three"])
    resource_id = FuzzyText()
    weblink = Sequence(lambda n: f"https://www.example.com/{n}")

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

    company = FuzzyText()
    contact_type = FuzzyChoice(["one", "two"])
    email = Sequence(lambda n: f"user{n}@example.com")
    is_active = Faker().pybool()
    is_external = Faker().pybool()
    notes = FuzzyText()
    owner = Sequence(lambda n: f"user{n}@example.com")

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


class TagTypeFactory(BaseFactory):
    """Tag Type Factory."""

    name = Sequence(lambda n: f"tag{n}")
    description = FuzzyText()
    project = SubFactory(ProjectFactory)

    class Meta:
        """Factory Configuration."""

        model = TagType


class TagFactory(BaseFactory):
    """Tag Factory."""

    name = Sequence(lambda n: f"tag{n}")
    uri = Sequence(lambda n: f"https://example.com/{n}")
    source = "foobar"
    discoverable = Faker().pybool()
    tag_type = SubFactory(TagTypeFactory)
    project = SubFactory(ProjectFactory)

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
    project = SubFactory(ProjectFactory)

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
    evergreen = Faker().pybool()
    evergreen_owner = FuzzyText()
    evergreen_reminder_interval = FuzzyInteger(low=0, high=100)
    evergreen_last_reminder_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))

    class Meta:
        """Factory Configuration."""

        model = Document

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id

    @post_generation
    def report(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.report_id = extracted.id

    @post_generation
    def filters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for filter in extracted:
                self.filters.append(filter)


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
    project = SubFactory(ProjectFactory)

    class Meta:
        """Factory Configuration."""

        model = IncidentPriority


class IncidentTypeFactory(BaseFactory):
    """Incident Type Factory."""

    name = FuzzyText()
    description = FuzzyText()
    slug = FuzzyText()
    project = SubFactory(ProjectFactory)

    class Meta:
        """Factory Configuration."""

        model = IncidentType


class IncidentRoleFactory(BaseFactory):
    """Incident Role Factory."""

    role = FuzzyChoice(["Incident Commander", "Scribe", "Liaison"])
    order = FuzzyInteger(low=1, high=10)
    enabled = True
    project = SubFactory(ProjectFactory)

    class Meta:
        """Factory configuration."""

        model = IncidentRole

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
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.append(tag)

    @post_generation
    def service(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.service_id = extracted.id

    @post_generation
    def individual(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.individual_id = extracted.id


class IndividualContactFactory(ContactBaseFactory):
    """Individual Contact Factory."""

    mobile_phone = "111-111-1111"
    name = Sequence(lambda n: f"Joe{n}")
    office_phone = "111-111-1111"
    project = SubFactory(ProjectFactory)
    title = FuzzyText()
    weblink = Sequence(lambda n: f"https://www.example.com/{n}")

    class Meta:
        """Factory Configuration."""

        model = IndividualContact


class ParticipantRoleFactory(BaseFactory):
    """Participant Factory."""

    assumed_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    renounced_at = None
    role = FuzzyChoice(["Incident Commander", "Reporter", "Scribe", "Liaison", "Participant"])

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

    team = Sequence(lambda n: f"team{n}")
    department = Sequence(lambda n: f"department{n}")
    location = Sequence(lambda n: f"location{n}")
    added_reason = Sequence(lambda n: f"added_reason{n}")
    after_hours_notification = Faker().pybool()

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
    def service(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.service_id = extracted.id

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


class RecommendationMatchFactory(BaseFactory):
    """Recommendation Accuracy Factory."""

    correct = True
    resource_type = ""
    resource_state = {}

    class Meta:
        """Factory Configuration."""

        model = RecommendationMatch

    @post_generation
    def recommendation(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.recommended_id = extracted.id


class RecommendationFactory(BaseFactory):
    """Recommendation Factory."""

    matches = [SubFactory(RecommendationMatch)]

    class Meta:
        """Factory Configuration."""

        model = Recommendation


class ServiceFactory(TimeStampBaseFactory):
    """Service Factory."""

    is_active = True
    name = Sequence(lambda n: f"service{n}")
    external_id = FuzzyText()
    project = SubFactory(ProjectFactory)

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
    document = SubFactory(DocumentFactory)

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

    resource_id = Sequence(lambda n: f"resource_id{n}")
    resource_type = Sequence(lambda n: f"resource_type{n}")
    weblink = Sequence(lambda n: f"https://www.example.com/{n}")

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id


class IncidentFactory(BaseFactory):
    """Incident Factory."""

    id = Sequence(lambda n: f"1{n}")
    name = FuzzyText()
    title = FuzzyText()
    description = FuzzyText()
    status = FuzzyChoice(["Active", "Stable", "Closed"])
    project = SubFactory(ProjectFactory)

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


class TaskFactory(ResourceBaseFactory):
    """Task Factory."""

    description = FuzzyText()
    last_reminder_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    priority = FuzzyChoice(["Low", "Medium", "High"])
    reminders = Faker().pybool()
    resolve_by = FuzzyDateTime(datetime(2020, 1, 2, tzinfo=UTC))
    resolved_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    source = FuzzyChoice(["Incident", "Post Incident Review"])
    status = FuzzyChoice(["Open", "Resolved"])
    incident = SubFactory(IncidentFactory)

    class Meta:
        """Factory Configuration."""

        model = Task

    @post_generation
    def creator(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.creator_id = extracted.id

    @post_generation
    def owner(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.owner_id = extracted.id

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id

    @post_generation
    def assignees(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for assignee in extracted:
                self.assignees.append(assignee)

    @post_generation
    def tickets(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for ticket in extracted:
                self.tickets.append(ticket)


class TeamContactFactory(ContactBaseFactory):
    """Team Contact Factory."""

    name = Sequence(lambda n: f"team{n}")
    notes = FuzzyText()
    project = SubFactory(ProjectFactory)

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
    def filters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for filter in extracted:
                self.filters.append(filter)


class TermFactory(BaseFactory):
    """Term Factory."""

    text = FuzzyText()
    discoverable = Faker().pybool()
    project = SubFactory(ProjectFactory)

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

    conference_id = Sequence(lambda n: f"conference{n}")
    conference_challenge = FuzzyText()
    incident = SubFactory(IncidentFactory)

    class Meta:
        """Factory Configuration."""

        model = Conference


class FeedbackFactory(BaseFactory):
    """Feedback Factory."""

    created_at = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=UTC))
    rating = FuzzyChoice(
        [
            "Very satisfied",
            "Somewhat satisfied",
            "Neither satisfied nor dissatisfied",
            "Somewhat dissatisfied",
            "Very dissatisfied",
        ]
    )
    feedback = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = Feedback

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


class IncidentCostFactory(BaseFactory):
    """Incident Cost Factory."""

    amount = FuzzyInteger(low=0, high=10000)

    class Meta:
        """Factory Configuration."""

        model = IncidentCost

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id

    @post_generation
    def incident_cost_type(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_cost_type_id = extracted.id


class IncidentCostTypeFactory(BaseFactory):
    """Incident Cost Type Factory."""

    name = FuzzyText()
    description = FuzzyText()
    category = FuzzyText()
    details = {}
    default = Faker().pybool()
    editable = Faker().pybool()

    class Meta:
        """Factory Configuration."""

        model = IncidentCostType


class NotificationFactory(BaseFactory):
    """Notification Factory."""

    name = FuzzyText()
    description = FuzzyText()
    type = FuzzyChoice(["email", "conversation"])
    target = FuzzyText()
    enabled = Faker().pybool()

    class Meta:
        """Factory Configuration."""

        model = Notification

    @post_generation
    def filters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for filter in extracted:
                self.filters.append(filter)


class SearchFilterFactory(BaseFactory):
    """Search Filter Factory."""

    name = FuzzyText()
    description = FuzzyText()
    expression = [{}]
    type = FuzzyText()

    class Meta:
        """Factory Configuration."""

        model = SearchFilter

    @post_generation
    def creator(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.creator_id = extracted.id


class PluginFactory(BaseFactory):
    """Plugin Factory."""

    title = FuzzyText()
    slug = FuzzyText()
    description = FuzzyText()
    version = FuzzyText()
    author = FuzzyText()
    author_url = FuzzyText()
    type = FuzzyText()
    multiple = Faker().pybool()

    class Meta:
        """Factory Configuration."""

        model = Plugin


class PluginInstanceFactory(BaseFactory):
    """PluginInstance Factory."""

    enabled = Faker().pybool()
    configuration = {}
    project = SubFactory(ProjectFactory)
    plugin = SubFactory(PluginFactory)

    class Meta:
        """Factory Configuration."""

        model = PluginInstance


class WorkflowFactory(BaseFactory):
    """Workflow Factory."""

    name = FuzzyText()
    description = FuzzyText()
    enabled = Faker().pybool()
    parameters = [{}]
    resource_id = Sequence(lambda n: f"resource_id{n}")

    class Meta:
        """Factory Configuration."""

        model = Workflow

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

    @post_generation
    def plugin_instance(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.plugin_instance_id = extracted.id


class WorkflowInstanceFactory(BaseFactory):
    """WorkflowInstance Factory."""

    parameters = [{}]
    run_reason = FuzzyText()
    status = FuzzyChoice(["Submitted", "Created", "Running", "Completed", "Failed"])

    class Meta:
        """Factory Configuration."""

        model = WorkflowInstance

    @post_generation
    def artifacts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for artifact in extracted:
                self.artifacts.append(artifact)

    @post_generation
    def workflow(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.workflow_id = extracted.id

    @post_generation
    def incident(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.incident_id = extracted.id

    @post_generation
    def creator(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.creator_id = extracted.id
