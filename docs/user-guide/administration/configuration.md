---
description: Configure Dispatch
---

# Configuration

Make Dispatch yours! Below you will find documentation surrounding the available configuration options available to you and what they mean for the incident process.

## Incident Types

Dispatch allows you to define your own incident types. These are used to bucket or categorize your incidents and map various other Dispatch resources(e.g. services and individuals) to these types.

To create a new incident type navigate to: `Dispatch > Incident Types > New`

![](../../.gitbook/assets/admin-ui-incident-types.png)

**Name:** The name of the incident type presented to the user.

**Description:** The description of the incident type presented to the user.

**Visibility:** Determines whether to send notification messages about this incident (creation and updates). Defaults to 'Open'.

**Service:** Defines the oncall service to use, in order to resolve an incident commander. Incident commander defaults to the `reporter` no service is set.

**Document:** Allows you to specify a incident document template to be created and filled for this incident type. This is useful if you like to use different document templates depending on the type of incident.

**Exclude From Metrics:** If for some reason you would like to exclude all incidents of this type from metrics (e.g. "Simulation" or "Test" incidents).

**Default Incident Type:** Check this if you would like for this incident to be the default type if the reporter does not specify.

## Incident Priorities

In addition to Incident Types, Dispatch allows you to specify the incident's _priority_.

To create a new incident priority navigate to: `Dispatch > Incident Priorities > New`

![](../../.gitbook/assets/admin-ui-incident-priorities.png)

**Name:** The name of the incident priority presented to the user.

**Description:** The incident priority description presented to the user.

**View Order:** The ranked order which the priority should be listed in menus and dropdowns.

**Tactical Report Reminder:** Number of hours between reminders.

**Executive Report Reminder:** Number of hours between reminders.

**Default Incident Priority:** Marks this priority as the default if the reporter does not specify.

**Page Commander:** Ensures that the incident commander is paged for all incidents with this priority (if configured paging service and plugin allows)

## Plugins

Much of Dispatch's functionality comes from it's plugins. The plugin's configuration UI is limited to enabling and disabling plugins. By default, no plugins are _required_ in order to create an incident. As you enable plugins, they will be additive to the incident process (e.g. creating slack channels, google docs etc.)

![](../../.gitbook/assets/admin-ui-incident-plugins.png)

Looking to add your own functionality to Dispatch via plugins? See the [contributing](../../contributing/plugins/README.md) documentation.

## Workflows

Workflows allows you to extend Dispatch, invoking you're own response automation. Dispatch does not currently include the ability to author workflows directly. Instead, the workflow functionality allows for exisiting workflows to be invoked from Dispatch. We rely on external workflow orchastration tools to execute those workflows, with Dispatch keeping track of resulting artifacts and workflow status.

To create a new incident workflow navigate to: `Dispatch > Workflows > New`

![](../../.gitbook/assets/admin-ui-incident-workflows.png)

**Name:** The name you wish to present to the user.

**Description:** The description presented to the user when the workflow is viewed.

**Resource Id:** The _external_ resource id used by Dispatch to associate the workflow with an external system.

**Plugin:** The plugin to use to resolve and execute this workflow. NOTE: This plugin must be enabled and installed before being associated with workflow.

**Enabled:** When disabled the workflow will not be selectabled by users.

**Workflow Parameters:** Allows for custom parameters (strings only) to be presented to the user that will then be passed to the underlying workflow.

## Users

Users represent users of the Dispatch UI and are different from individual contacts or incident participants. These user accounts are used to control access to the Dispatch UI only. We do not currently support creation or removal of users via the Dispatch UI, except in the case of self registration.

![](../../.gitbook/assets/admin-ui-incident-users.png)

**Role:** Dispatch uses role based access control (RBAC) for it's UI. Currently, this is only used to protect sensitive (Visibility: Closed) incidents. We do not currently have any controls surrounding Dispatch configuration and settings.

There are three roles defined by Dispatch:

- Admin - allows full access to the Dispatch UI.
- Poweruser - currently the same as Admin
- User - restricts access to sensitive incident (unless they are a direct participant).
