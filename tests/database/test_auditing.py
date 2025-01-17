from datetime import datetime, timezone
from pydantic import BaseModel
from dispatch.database.core import serialize_value, track_changes
from unittest.mock import Mock, MagicMock
from dispatch.auth.models import DispatchUser


# Sample Pydantic model for testing
class SampleModel(BaseModel):
    name: str
    created_at: datetime


# Test serialize_value function
def test_serialize_value_none():
    assert serialize_value(None) is None


def test_serialize_value_datetime_naive():
    dt = datetime(2023, 10, 1, 12, 0, 0)
    assert serialize_value(dt) == "2023-10-01T12:00:00"


def test_serialize_value_datetime_aware():
    dt = datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert serialize_value(dt) == "2023-10-01T12:00:00"


def test_serialize_value_pydantic_model():
    model = SampleModel(name="Test", created_at=datetime(2023, 10, 1, 12, 0, 0))
    expected = {"name": "Test", "created_at": "2023-10-01T12:00:00"}
    assert serialize_value(model) == expected


def test_serialize_value_dict():
    data = {"key": datetime(2023, 10, 1, 12, 0, 0)}
    expected = {"key": "2023-10-01T12:00:00"}
    assert serialize_value(data) == expected


def test_serialize_value_list():
    data = [datetime(2023, 10, 1, 12, 0, 0)]
    expected = ["2023-10-01T12:00:00"]
    assert serialize_value(data) == expected


def test_serialize_value_basic_types():
    assert serialize_value(123) == 123
    assert serialize_value(45.67) == 45.67
    assert serialize_value("string") == "string"


# Test track_changes function
def test_track_changes(mocker):
    # Mock session and instance
    mock_session = Mock()
    mock_instance = Mock()
    mock_instance.__class__.__name__ = "Signal"
    mock_instance.__tablename__ = "signal"
    # Mock session and instance
    mock_session = Mock()
    mock_instance = Mock()
    mock_instance.__class__.__name__ = "Signal"
    mock_instance.__tablename__ = "signal"

    # Mock state and history
    mock_state = Mock()
    mock_attrs = {"id": Mock(), "name": Mock()}
    mock_attrs["id"].key = "id"
    mock_attrs["name"].key = "name"
    mock_state.attrs = mock_attrs.values()  # Make attrs iterable

    # Mock get_history to return lists for deleted and added
    def mock_get_history(key, _):
        if key == "id":
            return Mock(unchanged=[1], deleted=[], added=[])
        elif key == "name":
            return Mock(deleted=["old_name"], added=["new_name"])

    mock_state.get_history.side_effect = mock_get_history

    # Mock inspect function
    def mock_inspect(instance):
        return mock_state

    # Mock session.dirty to return the mock instance
    mock_session.dirty = [mock_instance]

    # Create a mock DispatchUser
    mock_user = DispatchUser(
        id=1,
        email="test@example.com",
        password=b"hashed_password",
        experimental_features=False,
    )

    # Set the user attribute on the session
    mock_session.user = mock_user

    # Mock the context manager for no_autoflush
    mock_session.no_autoflush = MagicMock()  # Use MagicMock to support context manager

    # Call track_changes with the mock inspect function
    track_changes(mock_session, None, None, inspect=mock_inspect)

    # Check that changes were detected and logged
    assert mock_session.add.called, "Expected session.add to be called, but it was not."
    log_entry = mock_session.add.call_args[0][0]
    assert log_entry.table_name == "Signal"
    assert log_entry.changed_data == {"Signal.name": {"old": "old_name", "new": "new_name"}}
    assert log_entry.record_id == 1
    assert log_entry.dispatch_user == mock_user
