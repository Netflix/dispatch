import os
import os.path
import traceback
from subprocess import check_output

try:
    VERSION = __import__("pkg_resources").get_distribution("dispatch").version
except Exception:
    VERSION = "unknown"

# fix is in the works see: https://github.com/mpdavis/python-jose/pull/207
import warnings

warnings.filterwarnings("ignore", message="int_from_bytes is deprecated")

# sometimes we pull version info before dispatch is totally installed
try:
    from dispatch.organization.models import Organization  # noqa lgtm[py/unused-import]
    from dispatch.project.models import Project  # noqa lgtm[py/unused-import]
    from dispatch.route.models import Recommendation  # noqa lgtm[py/unused-import]
    from dispatch.conference.models import Conference  # noqa lgtm[py/unused-import]
    from dispatch.conversation.models import Conversation  # noqa lgtm[py/unused-import]
    from dispatch.cost_model.models import (
        CostModel,  # noqa lgtm[py/unused-import]
        CostModelActivity,  # noqa lgtm[py/unused-import]
    )
    from dispatch.definition.models import Definition  # noqa lgtm[py/unused-import]
    from dispatch.document.models import Document  # noqa lgtm[py/unused-import]
    from dispatch.event.models import Event  # noqa lgtm[py/unused-import]
    from dispatch.incident.models import Incident  # noqa lgtm[py/unused-import]
    from dispatch.monitor.models import Monitor  # noqa lgtm[py/unused-import]
    from dispatch.feedback.incident.models import Feedback  # noqa lgtm[py/unused-import]
    from dispatch.feedback.service.models import ServiceFeedback  # noqa lgtm[py/unused-import]
    from dispatch.group.models import Group  # noqa lgtm[py/unused-import]
    from dispatch.incident_cost.models import IncidentCost  # noqa lgtm[py/unused-import]
    from dispatch.incident_cost_type.models import IncidentCostType  # noqa lgtm[py/unused-import]
    from dispatch.incident_role.models import IncidentRole  # noqa lgtm[py/unused-import]
    from dispatch.incident.priority.models import IncidentPriority  # noqa lgtm[py/unused-import]
    from dispatch.incident.severity.models import IncidentSeverity  # noqa lgtm[py/unused-import]
    from dispatch.incident.type.models import IncidentType  # noqa lgtm[py/unused-import]
    from dispatch.individual.models import IndividualContact  # noqa lgtm[py/unused-import]
    from dispatch.notification.models import Notification  # noqa lgtm[py/unused-import]
    from dispatch.participant.models import Participant  # noqa lgtm[py/unused-import]
    from dispatch.participant_activity.models import (
        ParticipantActivity,  # noqa lgtm[py/unused-import]
    )
    from dispatch.participant_role.models import ParticipantRole  # noqa lgtm[py/unused-import]
    from dispatch.plugin.models import Plugin, PluginEvent  # noqa lgtm[py/unused-import]
    from dispatch.report.models import Report  # noqa lgtm[py/unused-import]
    from dispatch.service.models import Service  # noqa lgtm[py/unused-import]
    from dispatch.storage.models import Storage  # noqa lgtm[py/unused-import]
    from dispatch.tag.models import Tag  # noqa lgtm[py/unused-import]
    from dispatch.tag_type.models import TagType  # noqa lgtm[py/unused-import]
    from dispatch.task.models import Task  # noqa lgtm[py/unused-import]
    from dispatch.team.models import TeamContact  # noqa lgtm[py/unused-import]
    from dispatch.term.models import Term  # noqa lgtm[py/unused-import]
    from dispatch.ticket.models import Ticket  # noqa lgtm[py/unused-import]
    from dispatch.workflow.models import Workflow  # noqa lgtm[py/unused-import]
    from dispatch.data.source.status.models import SourceStatus  # noqa lgtm[py/unused-import]
    from dispatch.data.source.transport.models import SourceTransport  # noqa lgtm[py/unused-import]
    from dispatch.data.source.type.models import SourceType  # noqa lgtm[py/unused-import]
    from dispatch.data.alert.models import Alert  # noqa lgtm[py/unused-import]
    from dispatch.data.query.models import Query  # noqa lgtm[py/unused-import]
    from dispatch.data.source.models import Source  # noqa lgtm[py/unused-import]
    from dispatch.search_filter.models import SearchFilter  # noqa lgtm[py/unused-impot]
    from dispatch.case.models import Case  # noqa lgtm[py/unused-impot]
    from dispatch.case.priority.models import CasePriority  # noqa lgtm[py/unused-import]
    from dispatch.case.severity.models import CaseSeverity  # noqa lgtm[py/unused-import]
    from dispatch.case.type.models import CaseType  # noqa lgtm[py/unused-import]
    from dispatch.signal.models import Signal  # noqa lgtm[py/unused-import]
    from dispatch.feedback.service.reminder.models import (
        ServiceFeedbackReminder,  # noqa lgtm[py/unused-import]
    )
    from dispatch.forms.type.models import FormsType  # noqa lgtm[py/unused-import]
    from dispatch.forms.models import Forms  # noqa lgtm[py/unused-import]


except Exception:
    traceback.print_exc()


def _get_git_revision(path):
    if not os.path.exists(os.path.join(path, ".git")):
        return None
    try:
        revision = check_output(["git", "rev-parse", "HEAD"], cwd=path, env=os.environ)
    except Exception:
        # binary didn't exist, wasn't on path, etc
        return None
    return revision.decode("utf-8").strip()


def get_revision():
    """
    :returns: Revision number of this branch/checkout, if available. None if
        no revision number can be determined.
    """
    if "DISPATCH_BUILD" in os.environ:
        return os.environ["DISPATCH_BUILD"]
    package_dir = os.path.dirname(__file__)
    checkout_dir = os.path.normpath(os.path.join(package_dir, os.pardir, os.pardir))
    path = os.path.join(checkout_dir)
    if os.path.exists(path):
        return _get_git_revision(path)
    return None


def get_version():
    if __build__:
        return f"{__version__}.{__build__}"
    return __version__


def is_docker():
    # One of these environment variables are guaranteed to exist
    # from our official docker images.
    # DISPATCH_VERSION is from a tagged release, and DISPATCH_BUILD is from a
    # a git based image.
    return "DISPATCH_VERSION" in os.environ or "DISPATCH_BUILD" in os.environ


__version__ = VERSION
__build__ = get_revision()
