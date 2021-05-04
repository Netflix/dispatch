## Individual

In Dispatch, Individuals are either internal or external people identifiers. Typically, an organization will maintain a robust internal directory for user identities. Dispatch does not expect to replace those data stores. Instead, it keeps a lightweight notion of identities to associate with incidents for filtering and metrics.

It's common for incident response teams to maintain a list of contacts and run books to specify whom to contact when an incident occurs. Dispatch handles this for incident response teams by pulling the right individuals directly into an incident. By assigning terms, incident types, or incident priorities to individuals, Dispatch can instantly add them to the incident \(if internal\) or suggest reaching out to them \(if external\).

![](../../../.gitbook/assets/admin-ui-contacts-individuals.png)

**Name:** Name of the individual.

**Email:** Email address associated with the individual.

**Company:** Company associated with the individual.

#### Engagement

In addition to fields about the individual, Dispatch allows you to associate the individual with other Dispatch primitives. For instance, if you would like to involve an individual for all incidents of a given priority, associate that priority with the individual.
