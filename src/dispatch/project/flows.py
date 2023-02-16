from dispatch.case.priority import service as case_priority_service
from dispatch.case.priority.config import default_case_priorities
from dispatch.case.priority.models import CasePriorityCreate
from dispatch.case.severity import service as case_severity_service
from dispatch.case.severity.config import default_case_severities
from dispatch.case.severity.models import CaseSeverityCreate
from dispatch.case.type import service as case_type_service
from dispatch.case.type.config import default_case_type
from dispatch.case.type.models import CaseTypeCreate
from dispatch.decorators import background_task
from dispatch.incident.priority import service as incident_priority_service
from dispatch.incident.priority.config import default_incident_priorities
from dispatch.incident.priority.models import IncidentPriorityCreate
from dispatch.incident.severity import service as incident_severity_service
from dispatch.incident.severity.config import default_incident_severities
from dispatch.incident.severity.models import IncidentSeverityCreate
from dispatch.incident.type import service as incident_type_service
from dispatch.incident.type.config import default_incident_type
from dispatch.incident.type.models import IncidentTypeCreate
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.incident_cost_type.config import default_incident_cost_type
from dispatch.incident_cost_type.models import IncidentCostTypeCreate
from dispatch.plugin import service as plugin_service
from dispatch.plugin.models import PluginInstanceCreate

from .service import get


@background_task
def project_init_flow(*, project_id: int, organization_slug: str, db_session=None):
    """Initializes a new project with default settings."""
    project = get(db_session=db_session, project_id=project_id)

    # Add all plugins in disabled mode
    plugins = plugin_service.get_all(db_session=db_session)
    for plugin in plugins:
        plugin_instance_in = PluginInstanceCreate(
            project=project, plugin=plugin, configuration={}, enabled=False
        )
        plugin_service.create_instance(db_session=db_session, plugin_instance_in=plugin_instance_in)

    # Create default incident type
    incident_type_in = IncidentTypeCreate(
        name=default_incident_type["name"],
        description=default_incident_type["description"],
        visibility=default_incident_type["visibility"],
        exclude_from_metrics=default_incident_type["exclude_from_metrics"],
        default=default_incident_type["default"],
        enabled=default_incident_type["enabled"],
        project=project,
    )
    incident_type = incident_type_service.create(
        db_session=db_session, incident_type_in=incident_type_in
    )

    # Create default incident priorities
    for priority in default_incident_priorities:
        incident_priority_in = IncidentPriorityCreate(
            name=priority["name"],
            description=priority["description"],
            page_commander=priority["page_commander"],
            tactical_report_reminder=priority["tactical_report_reminder"],
            executive_report_reminder=priority["executive_report_reminder"],
            project=project,
            default=priority["default"],
            enabled=priority["enabled"],
            view_order=priority["view_order"],
            color=priority["color"],
        )
        incident_priority_service.create(
            db_session=db_session, incident_priority_in=incident_priority_in
        )

    # Create default incident severities
    for severity in default_incident_severities:
        incident_severity_in = IncidentSeverityCreate(
            name=severity["name"],
            description=severity["description"],
            project=project,
            default=severity["default"],
            enabled=severity["enabled"],
            view_order=severity["view_order"],
            color=severity["color"],
        )
        incident_severity_service.create(
            db_session=db_session, incident_severity_in=incident_severity_in
        )

    # Create default incident response cost
    incident_cost_type_in = IncidentCostTypeCreate(
        name=default_incident_cost_type["name"],
        description=default_incident_cost_type["description"],
        category=default_incident_cost_type["category"],
        details=default_incident_cost_type["details"],
        default=default_incident_cost_type["default"],
        editable=default_incident_cost_type["editable"],
        project=project,
    )
    incident_cost_type_service.create(
        db_session=db_session, incident_cost_type_in=incident_cost_type_in
    )

    # Create default case type
    case_type_in = CaseTypeCreate(
        name=default_case_type["name"],
        description=default_case_type["description"],
        visibility=default_case_type["visibility"],
        exclude_from_metrics=default_case_type["exclude_from_metrics"],
        default=default_case_type["default"],
        enabled=default_case_type["enabled"],
        project=project,
    )
    case_type = case_type_service.create(db_session=db_session, case_type_in=case_type_in)

    # Map case type with incident type
    case_type.incident_type = incident_type
    db_session.add(case_type)
    db_session.commit()

    # Create default case priorities
    for priority in default_case_priorities:
        case_priority_in = CasePriorityCreate(
            name=priority["name"],
            description=priority["description"],
            page_assignee=priority["page_assignee"],
            project=project,
            default=priority["default"],
            enabled=priority["enabled"],
            view_order=priority["view_order"],
            color=priority["color"],
        )
        case_priority_service.create(db_session=db_session, case_priority_in=case_priority_in)

    # Create default case severities
    for severity in default_case_severities:
        case_severity_in = CaseSeverityCreate(
            name=severity["name"],
            description=severity["description"],
            project=project,
            default=severity["default"],
            enabled=severity["enabled"],
            view_order=severity["view_order"],
            color=severity["color"],
        )
        case_severity_service.create(db_session=db_session, case_severity_in=case_severity_in)
