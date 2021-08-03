## Templates

Templates are special types of documents that are used by Dispatch to create incident specific documentation. These templates are copied and filled out to the best of Dispatch's abilities.

After creation they are normal documents that are associated to your incident which can be freely edited.

There are found main types of templates that Dispatch support's

- Incident
- Executive
- Review
- Tracking

Each type of template is fairly straightforward mapping directly to the incident response process. For example:

### Incident

This template is created for each new incident on incident creation. It contains the current state of the incident and is used by incident participants to share knowledge about the incident.

- [Example Incident Document](https://docs.google.com/document/d/1fv--CrGpWJJ4nyPR0N0hq4JchHJPuqsXN4azE9CGQiE)

### Executive

Often during an incident a executive report needs to be drafted that provides a high-level overview of the incident and the current actions that are being carried out. This template prompts the incident commander aids them in writing that communication.

- [Example Executive Report](https://docs.google.com/document/d/1dab6k14p5ageo5B_d1YlB_zS9hMGHDMXy9RUbIZous4)

### Review

The incident review document is automatically create (if it exist) when an incident is marked as stable. It is used by the incident commander and participants for reconciling any incident learnings or discussions.

- [Example Incident Review Document](https://docs.google.com/document/d/0-VwcEpVVdymoojdUg9e5XP8QGam0-B5Djxh-guuPpEc)

### Tracking

Some incidents require the tracking of multiple assets, this document is a simple spreadsheet document that allows incident participant to collaborate on tabular data.

- [Example Incident Tracking Sheet](https://docs.google.com/spreadsheets/d/1Odk4KlL7uMF_yd7OvTOCaPWmtTA_WzFBIA4lMeU5cGY)

### Template Variables

The following is a list of available variables that Dispatch will attempt to resolve on document creation (we do not currently re-resolve these).

NOTE: All variables must be enclosed in a `{{}}`

- `name` - The name of the incident
- `description` - The incidents description
- `title` - The incidents title
- `commander_fullname` - The current commanders name
- `type` - The incident type name
- `prioritity` - The incident priority name
- `status` - The incidents status
- `conversation_weblink` - Link to the conversation resource (if any)
- `conference_weblink` - Link to the conference resource (if any)
- `storage_weblink` - Link to the storage resource (if any)
- `document_weblink` - Link the incident document (if any)
- `ticket_weblink` - Link the incident ticket (if any)

### Association

Each of these documents can be associated on a per-incident type basis. This allows our templates to closely match a given incident type and provide additional context direction for those incident types.

Additionally, if you only desire one template; templates can be associated with multiple incident types.

![](../../../.gitbook/assets/admin-ui-create-edit-template.png)

**Name:** Name of the document.

**Description:** Short description of the document.

**Weblink:** A hyperlink representing the document.

**ID:** The external ID that is used to fetch the document.

### Evergreen

Enabling evergreen for a template instructs Dispatch to send an email reminder to the template owner, informing them that they should check to ensure that the template in question is up to date.
