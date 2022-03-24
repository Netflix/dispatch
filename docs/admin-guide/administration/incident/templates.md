## Templates

Templates are special types of documents that are used by Dispatch to create incident specific documentation. These templates are copied and filled out to the best of Dispatch's abilities.

After creation they are normal documents that are associated to your incident which can be freely edited.

There are four main types of templates that Dispatch supports:

- Incident
- Executive
- Review
- Tracking

Each type of template is fairly straightforward mapping directly to the incident response process. For example:

### Incident

A copy of this template is created for each new incident on incident creation. It contains the current state of the incident and is used by incident participants to share knowledge about the incident.

- [Example Incident Document](https://docs.google.com/document/d/1fv--CrGpWJJ4nyPR0N0hq4JchHJPuqsXN4azE9CGQiE)

### Executive

Often during an incident an executive report needs to be drafted that provides a high-level overview of the incident and the current actions that are being carried out. A copy of this template will be created, filled, and stored in the incident storage every time a new executive report is drafted.

- [Example Executive Report](https://docs.google.com/document/d/1dab6k14p5ageo5B_d1YlB_zS9hMGHDMXy9RUbIZous4)

### Review

A copy of this template is automatically created when an incident is marked as stable. It is used by the incident commander and participants for reconciling any incident learnings, discussions, or post-incident tasks.

- [Example Incident Review Document](https://docs.google.com/document/d/1MkCTyheZRtKzMxOBhLgh3PrvarERA9Bwo0joM7D9tmg)

### Tracking

Some incidents require the tracking of multiple assets, this template is a simple spreadsheet that allows incident participants to collaborate on tabular data.

- [Example Incident Tracking Sheet](https://docs.google.com/spreadsheets/d/1Odk4KlL7uMF_yd7OvTOCaPWmtTA_WzFBIA4lMeU5cGY)

### Template Variables

The following is a list of available variables that Dispatch will attempt to resolve on document creation. Note: we do not currently re-resolve these.

NOTE: All variables must be enclosed in a `{{}}`

- `name` - The name of the incident
- `title` - The incident's title
- `description` - The incident's description
- `resolution` - The incident's resolution
- `commander_fullname` - The current commander's name
- `type` - The incident's type name
- `prioritity` - The incident's priority name
- `status` - The incident's status
- `conversation_weblink` - Link to the conversation resource (if any)
- `conference_weblink` - Link to the conference resource (if any)
- `storage_weblink` - Link to the storage resource (if any)
- `document_weblink` - Link to the incident document (if any)
- `ticket_weblink` - Link to the incident ticket (if any)

### Association

Each of these templates can be associated on a per-incident type basis. This allows our templates to closely match a given incident type and provide additional context direction for those incident types.

Additionally, templates can be associated with multiple incident types, if for example, you only want to use one template.

![](../../../.gitbook/assets/admin-ui-create-edit-template.png)

**Name:** Name of the template.

**Description:** Short description of the template.

**Weblink:** The weblink to the template.

**ID:** The template's external ID used to fetch the document.

### Evergreen

Enabling evergreen for a template instructs Dispatch to send an email reminder to the template owner informing them that they should review the template to ensure that the template is up to date.
