---
description: Describes the plugin interface for each type of plugin.
---

# Interfaces

We do our best to keep this documentation up-to-date, however the code itself is still the best place to look for the most current documentation.

## Application

Applications, their names and associated metadata are important to incident response, Dispatch provides applications as first-class citizens and and either be entered manually through the Admin UI or via a `Application` plugin. The interface for this plugin is very simple:

```python
def get(self, **kwargs):
    return [{
        "name": "foo",
        "source": "bar",
        "uri": "example.com",
        "description": "A description"
    }]
```

Within Dispatch, any installed application plugins are run by the scheduler every \(1\) hour with task name `application-sync`.

## Conversation

Conversation plugins are deeply integrated within Dispatch. They server as the real-time communication channel used for incidents. By default Dispatch supports `Slack` as a conversation channel, if you wish to use another platform for conversations you will need to implement the following interface:

```python
def create(self, name: str, participants: List[dict], is_private: bool = True):
    """Creates a new conversation."""
    return {
        "id": "abc123",
        "name": "example",
        "weblink": "https://example.com"
    }

def send(
    self,
    conversation_id: str,
    text: str,
    message_template: dict,
    notification_type: str,
    items: Optional[List] = None,
    blocks: Optional[List] = None,
    persist: bool = False,
    **kwargs,
):
    """Sends a new message based on data and type."""
    return {
        "id": "abc123",
        "timestamp": "1232324384"
    }

def send_direct(
    self,
    user: str,
    text: str,
    message_template: dict,
    notification_type: str,
    items: Optional[List] = None,
    blocks: Optional[List] = None,
    **kwargs,
):
    """Sends a message directly to a user."""
    return {
        "id": "abc123",
        "timestamp": "1232324384"
    }

def send_ephemeral(
    self,
    conversation_id: str,
    user: str,
    text: str,
    message_template: dict = None,
    notification_type: str = None,
    items: Optional[List] = None,
    blocks: Optional[List] = None,
    **kwargs,
):
    """Sends an ephemeral message to a user in a channel."""
    return {
        "id": "abc123",
        "timestamp": "1232324384"
    }

def add(self, conversation_id: str, participants: List[str]):
    """Adds users to conversation."""
    return

def open_dialog(self, trigger_id: str, dialog: dict):
    """Opens a dialog with a user."""
    return

def open_modal(self, trigger_id: str, modal: dict):
    """Opens a modal with a user."""
    return

def archive(self, conversation_id: str):
    """Archives conversation."""
    return

def get_participant_username(self, participant_id: str):
    """Gets the participant's username."""
    return "username"

def get_participant_email(self, participant_id: str):
    """Gets the participant's email."""
    return "username@example.com"

def get_participant_avatar_url(self, participant_id: str):
    """Gets the participant's avatar url."""
    return "https://example.com/username.png"

def set_topic(self, conversation_id: str, topic: str):
    """Sets the conversation topic."""
    return

def get_command_name(self, command: str):
    """Gets the command name."""
    return "/some-command-name"
```

{% hint style="info" %}
Not all of the above functions will make sense for your conversation, but all are called by Dispatch in various flows, implement all of the functions for full functionality.,
{% endhint %}

## Document Resolver

Dispatch ships with an internal document resolver that attempts to gather documents related to an incident from within Dispatch's own document store. However, you may already have a robust external document store. It's interface is as follows:

```python
def get(
        self, incident_type: str, incident_priority: str, incident_description: str, db_session=None
    ):
    """Get documents related to the current incident."""
    return [{
           "name": "foo",
           "description": "bar",
           "weblink": "https://example.com/bar",
           "resource_type": "external-type",
           "resource_id": "abc123" }]
```

## Document

While there are other plugin interfaces for document management \(storage, resolution, etc.,\), this interface focuses solely on updating the document itself. This is used as part of the incident document template system; finding and replacing key terms and inject them incident specific information. Currently, we only ever update document using this interface:

```python
 def update(self, document_id: str, **kwargs):
     """Replaces text in document."""
     return
```

## Metric

The `metric` is an optional plugin that allows you to use whichever metric system that you have deployed within your organization.

```python
def gauge(self, name: str, value, tags=None):
    """Create a new gauge metric."""
    return

def counter(self, name: str, value=None, tags=None):
    """Create a new counter metric."""
    return

def timer(self, name: str, value, tags=None):
    """Create a new timer metric."""
    return
```

## Oncall

The on-call plugin is used to resolve or engage individuals directly. Dispatch ship's with support for `PagerDuty` but also provides this interface to add your own.

```python
def get(self, service_id: str = None, service_name: str = None):
    """Gets the oncall person."""
    return "joe@example.com"

def page(
    self, service_id: str, incident_name: str, incident_title: str, incident_description: str
):
    """Pages the oncall person."""
    return
```

## Participant Group

Often permissions for resources are manage by external entities or "groups". By default Dispatch uses Google Groups to help manage these permissions as these groups permission integrate nicely with the rest of the G Suite.

```python
def create(
        self, name: str, participants: List[str], description: str = None, role: str = "MEMBER"
    ):
    """Creates a new participant group."""
    return {
        "weblink": "https://example.com/my-incident",
        "email": "my-incident@example.com"
        "name": "my-incident"
    }

def add(self, email: str, participants: List[str], role: str = "MEMBER"):
    """Adds participants to existing participant group."""
    return

def remove(self, email: str, participants: List[str]):
    """Removes participants from existing participant group."""
    return

def delete(self, email: str):
    """Deletes an existing participant group."""
    return
```

## Participant

Similar to the document resolver plugin, Dispatch has the ability to pull in participants into incidents automatically. In order to accomplish this Dispatch ships with the `DispatchParticipantPlugin` which uses data internal to Dispatch \(services, individuals, teams\) to determine who should be involved with the incident itself.

```python
def get(
    self,
    incident_type: str,
    incident_priority: str,
    incident_description: str,
    db_session=None,
):
    """Fetches participants from Dispatch."""
    return
```

## Storage

By default, Dispatch uses Google Drive for all incident artifact storage. It provides a common interface for all incident participants and tight integration with the rest of G Suite.

Each incident get's it's own dedicated space \(a Team Drive in the case of Drive\). From there Dispatch expects the following interface when dealing with incident artifacts:

```python
def get(self, file_id: str, mime_type=None):
    """Fetches document text."""
    return "Document text"

def create(self, name: str, participants: List[str], role: str = Roles.file_organizer.value):
    """Creates a new drive."""
    return {
        "id": "abc123"
        "weblink": "https://example.com",
        "name": "example-drive"
        "description": "This is a drive"
    }

def delete(self, drive_id: str, empty: bool = True):
    """Deletes a drive."""
    return

def list(self, **kwargs):
    """Lists all available drives."""
    return [
        {
          "id": "abc123",
          "weblink": "https://example.com",
          "name": "example-drive"
          "description": "This is a drive"
        }
    }

def add_participant(
    self,
    drive_or_file_id: str,
    participants: List[str],
    role: str = "owner",
    user_type: str = "user",
):
    """Adds participants to existing drive."""
    return

def remove_participant(self, drive_id: str, participants: List[str]):
    """Removes participants from existing drive."""
    return

def create_file(self, drive_id: str, name: str, file_type: str = "folder"):
    """Creates a new file in existing drive."""
    return {
        "id": "abc123",
        "weblink": "https://example.com",
        "name": "file-name",
    }

def delete_file(self, drive_id: str, file_id: str):
    """Removes a file from existing drive."""
    return

def copy_file(self, drive_id: str, file_id: str, name: str):
    """Creates a copy of the given file and places it in the specified drive."""
    return {
        "id": "abc123",
        "weblink": "https://example.com",
        "name": "file-name",
    }

def move_file(self, new_drive_id: str, file_id: str):
    """Moves a file from one place to another."""
    return {
        "id": "abc123",
        "weblink": "https://example.com",
        "name": "file-name",
    }

def archive(self, source_drive_id, dest_folder_id, folder_name):
    """Archives a shared team drive to a specific folder."""
    return

def list_files(self, drive_id: str, q: str = None):
    """Lists all files in drive."""
    return [
        {
            "id": "abc123",
            "weblink": "https://example.com",
            "name": "file-name",
        }
    ]
```

## Task

{% hint style="info" %}
This interface is not stable and will need to be refactored and/or generalized. Please file an issue for guidance if you are trying to extend tasks.
{% endhint %}

Dispatch supports a lightweight tasking system to track incident tasks. By default this uses the G Suit comment system to assign, create and resolve tasks. If you have an external system you'd like Dispatch to monitor the following interface can be used:

```python
def list(self, file_id: str, **kwargs):
    """Lists all available tasks."""
    return
```

Dispatch scheduler will attempt to sync tasks every 30 seconds.

## Term

Term plugins are used for getting organization specific information within Dispatch from external systems and have a very simple interface:

```python
def get(self, **kwargs):
    return [{
        "text": "foo",
        "definitions": [{
            "text": "bar"
        }],
    }]
```

## Ticket

{% hint style="info" %}
This interface is not stable and will need to be refactored and/or generalized. Please file an issue for guidance if you are trying to extend ticket creation.
{% endhint %}

```python
def create(
        self, title: str, incident_type: str, incident_priority: str, commander: str, reporter: str
    ):
    """Creates a ticket."""
    return

def update(
    self,
    ticket_id: str,
    title: str = None,
    description: str = None,
    incident_type: str = None,
    priority: str = None,
    status: str = None,
    commander_email: str = None,
    reporter_email: str = None,
    conversation_weblink: str = None,
    document_weblink: str = None,
    storage_weblink: str = None,
    labels: List[str] = None,
    cost: str = None,
):
    """Updates ticket fields."""
    return
```

## Workflow

{% hint style="info" %}
This interface is not stable and will need to be refactored and/or generalized. Please file an issue for guidance if you are trying to extend workflow creation.
{% endhint %}

```python
def get_instance(
        self, workflow_id: str, instance_id: str, **kwargs)
    ):
    """Fetches an individual workflow instance."""
    return

def run(
    self,
    workflow_id: str, params: dict, **kwargs):
):
    """Runs the given workflow"""
    return
```
