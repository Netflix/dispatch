## Service

Like `Teams`, there are often groups of individuals (teams) responsible for an application or service that need to be involved in an incident. However, in these circumstances, we don't want to engage the _whole_ team. We only want to engage the individual that is on-call for the service. `Services` allow Dispatch to resolve these individuals via third-party on-call services (e.g., PagerDuty, OpsGenie).

![](../../../.gitbook/assets/admin-ui-contacts-services.png)

**Name:** Name of the service.

**Description:** Description of the service.

**Plugin:** The associated service plugin that Dispatch will use to resolve the on-call person.

**External Id:** The external ID used by Dispatch and the defined plugin to resolve the on-call person.

**Enabled:** Flag that determines if this particular service is active.

#### Engagement

In addition to the service fields, Dispatch allows you to associate the service with other Dispatch primitives. For instance, if you would like to involve a service for all incidents of a given priority, associate that priority with the service.
