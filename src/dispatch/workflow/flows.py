from dispatch.plugin import service as plugin_service


def send_workflow_notification(
    conversation_id,
    message_template,
    instance_status_old,
    instance_status_new,
    instance_weblink,
    instance_creator_name,
    workflow_name,
    workflow_description,
    db_session,
):
    """Sends a workflow notification."""
    notification_text = "Incident Notification"
    notification_type = "incident-notification"

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    plugin.instance.send(
        conversation_id,
        notification_text,
        message_template,
        notification_type,
        items=[
            {
                "instance_status_old": instance_status_old,
                "instance_status_new": instance_status_new,
                "instance_weblink": instance_weblink,
                "instance_creator_name": instance_creator_name,
                "workflow_name": workflow_name,
                "workflow_description": workflow_description,
            }
        ],
    )
