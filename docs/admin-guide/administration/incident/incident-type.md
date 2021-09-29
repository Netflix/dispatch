## Incident Types

Dispatch allows you to define incident types. Incident types bucket or categorize your incidents and map various other Dispatch resources (e.g., services and individuals) to these types.

![](../../../.gitbook/assets/admin-ui-incident-types.png)

**Name:** The name of the incident type presented to the user.

**Description:** The description of the incident type presented to the user.

**Visibility:** Allows you to specify how visible an incident of this type will be. For example, if `Open` is chosen, then notifications about an incident of this type will be sent on incident creation and update, and updates included on daily incident reports. All Dispatch users will be able to see incidents of this type in the Web UI regardless of their role. Also, Dispatch will use the Google domain provided to add organization-wide permission to the incident folder and its contents when the incident is marked as closed. However, if `Restricted` is chosen, incidents of this type will not be included in notifications, won't be visible to Dispatch users with a `member` role in the Web UI, and Dispatch won't open the incident folder and its contents to the whole organization. This setting defaults to `Open`.

**Service:** Allows you to define the on-call service to use to resolve an incident commander. The incident commander defaults to the `reporter` if no on-call service is defined.

**Document:** Allows you to specify an incident document template to be created and filled for this incident type. This is useful if you like to use different document templates depending on the type of incident.

**Exclude From Metrics:** Enable this setting to exclude all incidents of this type from metrics (e.g., "Simulation" or "Test" incidents).

**Default Incident Type:** If the reporter of an incident does not provide an incident type, a default incident type is used. Enable this setting to make this incident type the default.
