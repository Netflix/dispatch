## Incident Types

Dispatch allows you to define incident types. Incident types bucket or categorize your incidents and map various other Dispatch resources (e.g., services and individuals) to these types.

![](../../../.gitbook/assets/admin-ui-incident-types.png)

**Name:** The name of the incident type presented to the user.

**Description:** The description of the incident type presented to the user.

**Visibility:** Determines whether to send notification messages about this incident on creation and update. On incident close, this setting will add organization-wide permission to incident resources. Defaults to 'Open'.

**Service:** Defines the on-call service to use to resolve an incident commander. The incident commander defaults to the `reporter` if no on-call service is defined.

**Document:** Allows you to specify an incident document template to be created and filled for this incident type. This is useful if you like to use different document templates depending on the type of incident.

**Exclude From Metrics:** Enable this setting to exclude all incidents of this type from metrics (e.g., "Simulation" or "Test" incidents).

**Default Incident Type:** If the reporter of an incident does not provide an incident type, a default incident type is used. Enable this setting to make this incident type the default.
