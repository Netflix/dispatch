---
description: Overview of the Dispatch projects.
---

# Projects

Every incident within Dispatch is tied to a project. The project, and it's resources/configuration determines how the incident is run. This allows multiple teams to use Dispatch in different ways.

From having their own IncidentTypes and IncidentPriorities to providing the team with a view of their of their incident metrics. Projects drive this scoping of incidents.

### When should I create a new project vs using an existing one?

Generally, you would create a new project when the teams involved have very little overlap when handling incidents.

For example, you might create a `security` project for the handling of all security related incidents and a `reliability` project for all outage related incidents.

![](../../.gitbook/assets/admin-ui-project.png)

**Name:** The name you wish to give your project.

**Description:** A brief description of the project.
