import pytest
from sqlalchemy_utils import drop_database, database_exists
from starlette.config import environ
from starlette.testclient import TestClient

# set test config
environ["DATABASE_CREDENTIALS"] = "postgres:dispatch"
environ["DATABASE_HOSTNAME"] = "localhost"
environ["DATABASE_NAME"] = "dispatch-test"
environ["DISPATCH_ENCRYPTION_KEY"] = "test123"
environ["DISPATCH_JWT_SECRET"] = "test123"
environ["DISPATCH_UI_URL"] = "https://example.com"
environ["ENV"] = "pytest"
environ["JWKS_URL"] = "example.com"
environ["METRIC_PROVIDERS"] = ""  # TODO move this to the default
environ["SECRET_PROVIDER"] = ""
environ["STATIC_DIR"] = ""  # we don't need static files for tests

from dispatch import config
from dispatch.database.core import engine
from dispatch.database.manage import init_database

from .database import Session
from .factories import (
    CaseFactory,
    CaseCostFactory,
    CaseCostTypeFactory,
    CasePriorityFactory,
    CaseSeverityFactory,
    CaseTypeFactory,
    ConferenceFactory,
    ConversationFactory,
    DefinitionFactory,
    DispatchUserFactory,
    DocumentFactory,
    EntityFactory,
    EntityTypeFactory,
    EventFactory,
    FeedbackFactory,
    GroupFactory,
    IncidentCostFactory,
    CostModelFactory,
    CostModelActivityFactory,
    IncidentCostTypeFactory,
    IncidentFactory,
    IncidentPriorityFactory,
    IncidentRoleFactory,
    IncidentTypeFactory,
    IndividualContactFactory,
    NotificationFactory,
    OrganizationFactory,
    ParticipantActivityFactory,
    ParticipantFactory,
    ParticipantRoleFactory,
    PluginFactory,
    PluginEventFactory,
    PluginInstanceFactory,
    ProjectFactory,
    RecommendationFactory,
    RecommendationMatchFactory,
    ReportFactory,
    SearchFilterFactory,
    ServiceFactory,
    SignalFactory,
    SignalFilterFactory,
    SignalInstanceFactory,
    StorageFactory,
    TagFactory,
    TagTypeFactory,
    TaskFactory,
    TeamContactFactory,
    TermFactory,
    TicketFactory,
    WorkflowFactory,
    WorkflowInstanceFactory,
)


def pytest_runtest_setup(item):
    if "slow" in item.keywords and not item.config.getoption("--runslow"):
        pytest.skip("need --runslow option to run")

    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed ({0})".format(previousfailed.name))


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


@pytest.fixture(scope="session")
def testapp():
    # we only want to use test plugins so unregister everybody else
    from dispatch.main import app
    from dispatch.plugins.base import plugins, unregister

    for p in plugins.all():
        unregister(p)

    yield app


@pytest.fixture(scope="session")
def db():
    if database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        drop_database(str(config.SQLALCHEMY_DATABASE_URI))

    init_database(engine)
    schema_engine = engine.execution_options(
        schema_translate_map={
            None: "dispatch_organization_default",
            "dispatch_core": "dispatch_core",
        }
    )
    Session.configure(bind=schema_engine)
    yield
    drop_database(str(config.SQLALCHEMY_DATABASE_URI))


@pytest.fixture(scope="function", autouse=True)
def session(db):
    """
    Creates a new database session with (with working transaction)
    for test duration.
    """
    session = Session()
    session.begin_nested()
    yield session
    session.rollback()


@pytest.fixture(scope="function")
def client(testapp, session, client):
    yield TestClient(testapp)


@pytest.fixture
def conference_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.conference import TestConferencePlugin

    register(TestConferencePlugin)
    return TestConferencePlugin


@pytest.fixture
def contact_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.contact import TestContactPlugin

    register(TestContactPlugin)
    return TestContactPlugin


@pytest.fixture
def conversation_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.conversation import TestConversationPlugin

    register(TestConversationPlugin)
    return TestConversationPlugin


@pytest.fixture
def definition_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.definition import TestDefinitionPlugin

    register(TestDefinitionPlugin)
    return TestDefinitionPlugin


@pytest.fixture
def document_resolver_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.document_resolver import TestDocumentResolverPlugin

    register(TestDocumentResolverPlugin)
    return TestDocumentResolverPlugin


@pytest.fixture
def document_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.document import TestDocumentPlugin

    register(TestDocumentPlugin)
    return TestDocumentPlugin


@pytest.fixture
def oncall_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.oncall import TestOncallPlugin

    register(TestOncallPlugin)
    return TestOncallPlugin


@pytest.fixture
def participant_group_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.participant_group import TestParticipantGroupPlugin

    register(TestParticipantGroupPlugin)
    return TestParticipantGroupPlugin


@pytest.fixture
def participant_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.participant import TestParticipantPlugin

    register(TestParticipantPlugin)
    return TestParticipantPlugin


@pytest.fixture
def storage_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.storage import TestStoragePlugin

    register(TestStoragePlugin)
    return TestStoragePlugin


@pytest.fixture
def task_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.task import TestTaskPlugin

    register(TestTaskPlugin)
    return TestTaskPlugin


@pytest.fixture
def term_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.term import TestTermPlugin

    register(TestTermPlugin)
    return TestTermPlugin


@pytest.fixture
def ticket_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.ticket import TestTicketPlugin

    register(TestTicketPlugin)
    return TestTicketPlugin


@pytest.fixture
def workflow_plugin():
    from dispatch.plugins.base import register
    from dispatch.plugins.dispatch_test.workflow import TestWorkflowPlugin

    register(TestWorkflowPlugin)
    return TestWorkflowPlugin


@pytest.fixture
def user(session):
    return DispatchUserFactory()


@pytest.fixture
def tag(session):
    return TagFactory()


@pytest.fixture
def tag_type(session):
    return TagTypeFactory()


@pytest.fixture
def tag_types(session):
    return [TagTypeFactory(), TagTypeFactory()]


@pytest.fixture
def conference(session):
    return ConferenceFactory()


@pytest.fixture
def conferences(session):
    return [ConferenceFactory(), ConferenceFactory(), ConferenceFactory()]


@pytest.fixture
def conversation(session):
    return ConversationFactory()


@pytest.fixture
def conversations(session):
    return [ConversationFactory(), ConversationFactory()]


@pytest.fixture
def definition(session):
    return DefinitionFactory()


@pytest.fixture
def document(session):
    return DocumentFactory()


@pytest.fixture
def group(session):
    return GroupFactory()


@pytest.fixture
def groups(session):
    return [GroupFactory(), GroupFactory()]


@pytest.fixture
def incident_priority(session):
    return IncidentPriorityFactory()


@pytest.fixture
def incident_priorities(session):
    return [IncidentPriorityFactory(), IncidentPriorityFactory()]


@pytest.fixture
def incident_role(session):
    return IncidentRoleFactory()


@pytest.fixture
def incident_type(session):
    return IncidentTypeFactory()


@pytest.fixture
def incident_types(session):
    return [IncidentTypeFactory(), IncidentTypeFactory()]


@pytest.fixture
def individual_contact(session):
    return IndividualContactFactory()


@pytest.fixture
def participant_role(session):
    return ParticipantRoleFactory()


@pytest.fixture
def participant_roles(session):
    return [ParticipantRoleFactory(), ParticipantRoleFactory()]


@pytest.fixture
def participant(session):
    return ParticipantFactory(individual=IndividualContactFactory())


@pytest.fixture
def participants(session):
    return [ParticipantFactory(), ParticipantFactory()]


@pytest.fixture
def organization(session):
    return OrganizationFactory()


@pytest.fixture
def organizations(session):
    return [OrganizationFactory(), OrganizationFactory()]


@pytest.fixture
def project(session):
    return ProjectFactory()


@pytest.fixture
def projects(session):
    return [ProjectFactory(), ProjectFactory()]


@pytest.fixture
def recommendation_accuracy(session):
    return RecommendationMatchFactory()


@pytest.fixture
def recommendation(session):
    return RecommendationFactory()


@pytest.fixture
def service(session):
    return ServiceFactory()


@pytest.fixture
def services(session):
    return [ServiceFactory(), ServiceFactory()]


@pytest.fixture
def report(session):
    return ReportFactory()


@pytest.fixture
def reports(session):
    return [ReportFactory(), ReportFactory()]


@pytest.fixture()
def entity(session):
    return EntityFactory()


@pytest.fixture()
def entity_type(session):
    return EntityTypeFactory()


@pytest.fixture()
def entity_types(session):
    return [EntityTypeFactory(), EntityTypeFactory()]


@pytest.fixture()
def signal(session):
    return SignalFactory()


@pytest.fixture()
def signal_filter(session):
    return SignalFilterFactory()


@pytest.fixture()
def signal_instance(session):
    return SignalInstanceFactory()


@pytest.fixture
def storage(session):
    return StorageFactory()


@pytest.fixture
def storages(session):
    return [StorageFactory(), StorageFactory()]


@pytest.fixture
def task(session):
    return TaskFactory()


@pytest.fixture
def team_contact(session):
    return TeamContactFactory()


@pytest.fixture
def team_contacts(session):
    return [TeamContactFactory(), TeamContactFactory()]


@pytest.fixture
def term(session):
    return TermFactory()


@pytest.fixture
def ticket(session):
    return TicketFactory()


@pytest.fixture
def tickets(session):
    return [TicketFactory(), TicketFactory()]


@pytest.fixture
def case(session):
    return CaseFactory()


@pytest.fixture
def new_case(session):
    return CaseFactory(status="New")


@pytest.fixture
def case_priority(session):
    return CasePriorityFactory()


@pytest.fixture
def case_severity(session):
    return CaseSeverityFactory()


@pytest.fixture
def case_type(session):
    return CaseTypeFactory()


@pytest.fixture
def incident(session):
    return IncidentFactory()


@pytest.fixture
def participant_activity(session):
    return ParticipantActivityFactory()


@pytest.fixture
def event(session):
    return EventFactory()


@pytest.fixture
def events(session):
    return [EventFactory(), EventFactory()]


@pytest.fixture
def feedback(session):
    return FeedbackFactory()


@pytest.fixture
def feedbacks(session):
    return [FeedbackFactory(), FeedbackFactory()]


@pytest.fixture
def case_cost(session):
    return CaseCostFactory()


@pytest.fixture
def case_costs(session):
    return [CaseCostFactory(), CaseCostFactory()]


@pytest.fixture
def case_cost_type(session):
    return CaseCostTypeFactory()


@pytest.fixture
def incident_cost(session):
    return IncidentCostFactory()


@pytest.fixture
def incident_costs(session):
    return [IncidentCostFactory(), IncidentCostFactory()]


@pytest.fixture
def incident_cost_type(session):
    return IncidentCostTypeFactory()


@pytest.fixture
def incident_cost_types(session):
    return [IncidentCostTypeFactory(), IncidentCostTypeFactory()]


@pytest.fixture
def notification(session):
    return NotificationFactory()


@pytest.fixture
def notifications(session):
    return [NotificationFactory(), NotificationFactory()]


@pytest.fixture
def search_filter(session):
    return SearchFilterFactory()


@pytest.fixture
def search_filters(session):
    return [SearchFilterFactory(), SearchFilterFactory()]


@pytest.fixture
def plugin(session):
    return PluginFactory()


@pytest.fixture
def plugins(session):
    return [PluginFactory(), PluginFactory()]


@pytest.fixture
def plugin_instance(session):
    return PluginInstanceFactory()


@pytest.fixture
def conversation_plugin_instance(session, conversation_plugin):
    return PluginInstanceFactory(plugin=PluginFactory(slug=conversation_plugin.slug))


@pytest.fixture
def workflow_plugin_instance(session, workflow_plugin):
    return PluginInstanceFactory(plugin=PluginFactory(slug=workflow_plugin.slug))


@pytest.fixture
def workflow(session, workflow_plugin_instance):
    return WorkflowFactory(plugin_instance=workflow_plugin_instance)


@pytest.fixture
def workflow_instance(session):
    return WorkflowInstanceFactory()


@pytest.fixture
def plugin_event(session):
    return PluginEventFactory()


@pytest.fixture
def cost_model(session):
    return CostModelFactory()


@pytest.fixture
def cost_model_activity(session):
    return CostModelActivityFactory()
