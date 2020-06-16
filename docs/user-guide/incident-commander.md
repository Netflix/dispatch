---
description: What to expect as an incident commander.
---

# Incident Commander

## Reporting

Within Dispatch Incident Commander's \(ICs\) are also participants and will receive all of the messaging that a participant does. When resolved as incident commander you are assigned that role by Dispatch and your identity is propagated via various messaging. Additionally for `High` severity events, the Incident Commander is automatically paged \(via PagerDuty\).

## During

During an incident, the IC is responsible for pushing the incident forward and keeping the group going in the right direction. To help them with this, Dispatch provides a few useful commands:

### Roles

`/dispatch-assign-role`

You're not always incident commander forever, sometimes a situation changes or you just need a break. The `dispatch-assign-role` command makes it easy and more importantly _clear_ to everyone involved in the incident who the current incident commander is.

![](https://github.com/Netflix/dispatch/tree/2571e82ab72a58c36a41f8070e62550bded4ced0/docs/.gitbook/assets/slack-conversation-assign-role%20%281%29.png)

### Status

`/dispatch-list-participants`

This command is most useful for determining which teams are already engaged and who the IC commander might want to task or ask questions of.

![](https://github.com/Netflix/dispatch/tree/2571e82ab72a58c36a41f8070e62550bded4ced0/docs/.gitbook/assets/slack-conversation-list-participants%20%281%29.png)

`/dispatch-edit-incident`

This command allows the IC to modify several aspects of the incident without ever leaving the conversation interface.

![](https://github.com/Netflix/dispatch/tree/2571e82ab72a58c36a41f8070e62550bded4ced0/docs/.gitbook/assets/slack-conversation-edit-incident%20%281%29.png)

`/dispatch-status-report`

One of the most important aspects of an IC commanders job is notifying external stakeholders on the current state of the incident. These stakeholders should never be down in the weeds of incident management but do need a way to view concise and up-to-date incident information. The `status-report` command allows the IC to do so in a standardized way.

![](../.gitbook/assets/slack-conversation-status-report-response%20%281%29.png)

![](https://github.com/Netflix/dispatch/tree/2571e82ab72a58c36a41f8070e62550bded4ced0/docs/.gitbook/assets/slack-conversation-status-report%20%281%29.png)

### Tasks

During an incident you may want assign asks or ask questions. Dispatch provides a light weight tasking mechanism by integrating with the Google Docs commenting system.

In the Incident Document:

![](https://github.com/Netflix/dispatch/tree/2571e82ab72a58c36a41f8070e62550bded4ced0/docs/.gitbook/assets/google-docs-task-comment%20%281%29.png)

## After

Once the incident is stable or can be closed, Dispatch again provides a few helpful commands to the IC:

`/dispatch-mark-stable`

This command marks the incident as stable, updating external tickets as necessary.

It also creates a Post Incident Review \(PIR\) document to help you track the post incident review process.

`/dispatch-mark-closed`

The command marks the incident as close and begins cleaning up incident resources including, archiving incident documents, conversation channels and groups.

