## Documents

To create a new document navigate to: `Dispatch > Documents > New`

![](../../.gitbook/assets/admin-ui-knowledge-documents.png)

Documents are links to external sources \(Web Pages, Google Documents, etc.,\). These documents can be associated with terms, incident types, and incident priorities, allowing these documents to be recommended reading for incident participants.

If you use the Google Drive plugin, Dispatch will copy a Google document associated with an incident type into a folder. Make sure you specify the correct Google Docs ID for the `ID` field.

**Name:** Name of the document.

**Description:** Short description of the document.

**Weblink:** A hyperlink representing the document.

**ID:** The external ID that is used to fetch the document.

**Type:** A user-defined document type.

### Incident Templates

Documents can also be used as templates during incident creation that Dispatch will attempt to fill.

If you are using the Google Drive plugin, we provide a set of templates to get you started. These should be copied into your Google Drive and then created as documents in the Dispatch UI.

- [Incident Document](https://docs.google.com/document/d/1fv--CrGpWJJ4nyPR0N0hq4JchHJPuqsXN4azE9CGQiE)

- [Incident Review Document](https://docs.google.com/document/d/1-VwcEpVVdymoojdUg9e5XP8QGam0-B5Djxh-guuPpEc)

- [Executive Report](https://docs.google.com/document/d/1dab6k14p5ageo5B_d1YlB_zS9hMGHDMXy9RUbIZous4)

- [Incident Tracking Sheet](https://docs.google.com/spreadsheets/d/1Odk4KlL7uMF_yd7OvTOCaPWmtTA_WzFBIA4lMeU5cGY)

### Template variables

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

#### Engagement

In addition to fields about the document itself, Dispatch allows you to associate a document with other Dispatch primitives. For instance, if you would like a given document to be recommended for all incidents of a given priority, associate that priority with the document.

#### Evergreen

Enabling evergreen for a document instructs Dispatch to send an email reminder to the document owner, informing them that they should check to ensure that the document in question is up to date.
