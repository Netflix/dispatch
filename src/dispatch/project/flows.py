from dispatch.decorators import background_task
from dispatch.case.priority import service as case_priority_service
from dispatch.case.priority.config import default_case_priorities
from dispatch.case.priority.models import CasePriorityCreate
from dispatch.case.severity import service as case_severity_service
from dispatch.case.severity.config import default_case_severities
from dispatch.case.severity.models import CaseSeverityCreate
from dispatch.incident.priority import service as incident_priority_service
from dispatch.incident.priority.config import default_incident_priorities
from dispatch.incident.priority.models import IncidentPriorityCreate
from dispatch.incident.severity import service as incident_severity_service
from dispatch.incident.severity.config import default_incident_severities
from dispatch.incident.severity.models import IncidentSeverityCreate
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.incident_cost_type.config import default_incident_cost_type
from dispatch.incident_cost_type.models import IncidentCostTypeCreate
from dispatch.plugin import service as plugin_service
from dispatch.plugin.models import PluginInstanceCreate

from .service import get


@background_task
def project_create_flow(*, organization_slug: str, project_id: int, db_session=None):
    project = get(db_session=db_session, project_id=project_id)

    # Add all plugins in disabled mode
    plugins = plugin_service.get_all(db_session=db_session)
    for plugin in plugins:
        plugin_instance_in = PluginInstanceCreate(
            project=project, plugin=plugin, configuration={}, enabled=False
        )
        plugin_service.create_instance(db_session=db_session, plugin_instance_in=plugin_instance_in)

    # Create default incident priorities
    for priority in default_incident_priorities:
        incident_priority_in = IncidentPriorityCreate(**priority)
        incident_priority_service.create(
            db_session=db_session, incident_priority_in=incident_priority_in
        )

    # Create default incident severities
    for severity in default_incident_severities:
        incident_severity_in = IncidentSeverityCreate(**severity)
        incident_severity_service.create(
            db_session=db_session, incident_severity_in=incident_severity_in
        )

    # Create default incident response cost
    incident_cost_type_in = IncidentCostTypeCreate(**default_incident_cost_type, project=project)
    incident_cost_type_service.create(
        db_session=db_session, incident_cost_type_in=incident_cost_type_in
    )

    # Create default case priorities
    for priority in default_case_priorities:
        case_priority_in = CasePriorityCreate(**priority)
        case_priority_service.create(db_session=db_session, case_priority_in=case_priority_in)

    # Create default case severities
    for severity in default_case_severities:
        case_severity_in = CaseSeverityCreate(**severity)
        case_severity_service.create(db_session=db_session, case_severity_in=case_severity_in)
