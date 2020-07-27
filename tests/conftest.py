import pytest

from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.testclient import TestClient
from starlette.config import environ

# set test config
environ["DATABASE_CREDENTIALS"] = "postgres:dispatch"
environ["DATABASE_HOSTNAME"] = "localhost"
environ["DISPATCH_HELP_EMAIL"] = "example@example.com"
environ["DISPATCH_HELP_SLACK_CHANNEL"] = "help-me"
environ["DISPATCH_UI_URL"] = "https://example.com"
environ["SLACK_APP_USER_SLUG"] = "XXX"
environ["INCIDENT_NOTIFICATION_CONVERSATIONS"] = "sirt-dev-test-notify"
environ["INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS"] = "sirt-dev-test-notify@example.com"
environ["INCIDENT_STORAGE_FOLDER_ID"] = "XXX"
environ["JWKS_URL"] = "example.com"
environ["ENV"] = "pytest"
environ["DISPATCH_AUTHENTICATION_PROVIDER_SLUG"] = ""  # disable authentication for tests
environ["METRIC_PROVIDERS"] = ""  # TODO move this to the default
environ["STATIC_DIR"] = ""  # we don't need static files for tests

from dispatch import config
from dispatch.database import Base, engine, SessionLocal

from .factories import (
    ConferenceFactory,
    ConversationFactory,
    DefinitionFactory,
    DocumentFactory,
    EventFactory,
    GroupFactory,
    IncidentFactory,
    IncidentPriorityFactory,
    IncidentTypeFactory,
    IndividualContactFactory,
    ParticipantFactory,
    ParticipantRoleFactory,
    PolicyFactory,
    RecommendationAccuracyFactory,
    RecommendationFactory,
    ServiceFactory,
    ReportFactory,
    StorageFactory,
    TagFactory,
    TaskFactory,
    TeamContactFactory,
    TermFactory,
    TicketFactory,
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
    from dispatch.plugins.base import unregister, plugins
    from dispatch.main import app

    for p in plugins.all():
        unregister(p)

    yield app


@pytest.fixture(scope="session", autouse=True)
def db():
    if database_exists(str(config.SQLALCHEMY_DATABASE_URI)):
        drop_database(str(config.SQLALCHEMY_DATABASE_URI))

    create_database(str(config.SQLALCHEMY_DATABASE_URI))
    Base.metadata.create_all(engine)  # Create the tables.
    _db = SessionLocal()
    yield _db
    drop_database(str(config.SQLALCHEMY_DATABASE_URI))


@pytest.fixture(scope="function")
def session(db):
    """
    Creates a new database session with (with working transaction)
    for test duration.
    """
    db.begin_nested()
    yield db
    db.rollback()


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
def Tag(session):
    return TagFactory()


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
    return ParticipantFactory()


@pytest.fixture
def participants(session):
    return [ParticipantFactory(), ParticipantFactory()]


@pytest.fixture
def policy(session):
    return PolicyFactory()


@pytest.fixture
def recommendation_accuracy(session):
    return RecommendationAccuracyFactory()


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
def storage(session):
    return StorageFactory()


@pytest.fixture
def task(session):
    return TaskFactory()


@pytest.fixture
def team_contact(session):
    return TeamContactFactory()


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
def incident(session):
    return IncidentFactory()


@pytest.fixture
def event(session):
    return EventFactory()


@pytest.fixture
def events(session):
    return [EventFactory(), EventFactory()]
