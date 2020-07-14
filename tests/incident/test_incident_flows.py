import pytest


def test_update_external_incident_ticket(incident, session, ticket_plugin, incident_type, mocker):
    from dispatch.incident.flows import update_external_incident_ticket
    from dispatch.plugin import service as plugin_service

    # from dispatch.incident_type import service as incident_type_service

    mocker.patch.object(ticket_plugin, "update", {})
    mocker.patch.object(plugin_service, "get_active", ticket_plugin)
    # mocker.patch.object(incident_type_service, "get_by_name", )

    update_external_incident_ticket(incident=incident, db_session=session)

    ticket_plugin.update.assert_called_once_with(
        ticket_id=incident.ticket.resource_id,
        title=incident.title,
        description=incident.description,
        status=incident.status,
        cost=incident.cost,
        incident_type=incident.incident_type.name,
        incident_priority=incident.incident_priority.name,
        conversation=incident.conversation,
        storage=incident.storage,
        conference=incident.conference,
    )


def test_set_conversation_topic():
    pass


def test_update_document():
    pass
