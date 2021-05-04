## Tags

Within Dispatch, tags are a flexible piece of metadata. They can be manually attached to incidents or automatically discovered based on incident data.

![](../../../.gitbook/assets/admin-ui-knowledge-tags.png)

**Name:** The tag string itself, or what you would expect to be in incident data.

**Description:** A short description of the tag (if applicable).

**Type:** The type of the tag that will be used to disambiguate or categorize this tag from other tags. Tag types can be defined by users or plugins that syncing tags from external sources (e.g., application names).

**Source:** Where the tag originated. For tags created via the UI, Dispatch is the default source.

**URI:** The external tag locator (if available).

**Discoverable:** Dispatch can automatically discover tags. Meaning given a set of predefined tags, it will crawl all incident data available to it and, using NLP, associate this data to incidents (current incident and retroactively). If a tag is general enough (e.g., "the") that you do not want to make it discoverable, this flag can disable that functionality on an individual tag basis.
