import os
import os.path
from subprocess import check_output

try:
    VERSION = __import__("pkg_resources").get_distribution("dispatch").version
except Exception:
    VERSION = "unknown"

# sometimes we pull version info before dispatch is totally installed
try:
    from dispatch.conference.models import Conference  # noqa lgtm[py/unused-import]
    from dispatch.team.models import TeamContact  # noqa lgtm[py/unused-import]
    from dispatch.conversation.models import Conversation  # noqa lgtm[py/unused-import]
    from dispatch.definition.models import Definition  # noqa lgtm[py/unused-import]
    from dispatch.document.models import Document  # noqa lgtm[py/unused-import]
    from dispatch.event.models import Event  # noqa lgtm[py/unused-import]
    from dispatch.feedback.models import Feedback  # noqa lgtm[py/unused-import]
    from dispatch.group.models import Group  # noqa lgtm[py/unused-import]
    from dispatch.incident.models import Incident  # noqa lgtm[py/unused-import]
    from dispatch.incident_priority.models import IncidentPriority  # noqa lgtm[py/unused-import]
    from dispatch.incident_type.models import IncidentType  # noqa lgtm[py/unused-import]
    from dispatch.individual.models import IndividualContact  # noqa lgtm[py/unused-import]
    from dispatch.participant.models import Participant  # noqa lgtm[py/unused-import]
    from dispatch.participant_role.models import ParticipantRole  # noqa lgtm[py/unused-import]
    from dispatch.policy.models import Policy  # noqa lgtm[py/unused-import]
    from dispatch.route.models import (
        Recommendation,  # noqa lgtm[py/unused-import]
        RecommendationAccuracy,  # noqa lgtm[py/unused-import]
    )
    from dispatch.service.models import Service  # noqa lgtm[py/unused-import]
    from dispatch.report.models import Report  # noqa lgtm[py/unused-import]
    from dispatch.storage.models import Storage  # noqa lgtm[py/unused-import]
    from dispatch.tag.models import Tag  # noqa lgtm[py/unused-import]
    from dispatch.tag_type.models import TagType  # noqa lgtm[py/unused-import]
    from dispatch.task.models import Task  # noqa lgtm[py/unused-import]
    from dispatch.term.models import Term  # noqa lgtm[py/unused-import]
    from dispatch.ticket.models import Ticket  # noqa lgtm[py/unused-import]
    from dispatch.plugin.models import Plugin  # noqa lgtm[py/unused-import]
    from dispatch.workflow.models import Workflow  # noqa lgtm[py/unused-import]
except Exception:
    pass


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
