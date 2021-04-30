## Workflows

Workflows allow you to extend Dispatch, invoking your response automation. Dispatch does not currently include the ability to author workflows directly. Instead, the workflow functionality allows for existing workflows to be invoked from Dispatch. We rely on external workflow orchestration tools to execute those workflows, with Dispatch keeping track of resulting artifacts and workflow status.

![](../../../.gitbook/assets/admin-ui-incident-workflows.png)

**Name:** The name you wish to present to the user.

**Description:** The description presented to the user when the workflow is viewed.

**Resource Id:** The _external_ resource id used by Dispatch to associate the workflow with an external system.

**Plugin:** The plugin to use to resolve and execute this workflow. NOTE: This plugin must be enabled and installed before being associated with a workflow.

**Enabled:** By default, users can't invoke workflows. Activate the "Enabled" setting to allow the use of the workflow.

**Workflow Parameters:** Allows for custom parameters (strings only) to be presented to and set by the user. These are passed to the underlying workflow.
