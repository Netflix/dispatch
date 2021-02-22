---
description: What to expect as an incident participant.
---

# Incident Participant

## Reporting

Dispatch attempts to make reporting incidents as easy as possible. Dispatch provides a dedicated incident report form that users throughout the organization can submit to engage incident-related resources.

Located at: `https://<your-dispatch-domain>/incidents/report`

![](../.gitbook/assets/admin-ui-incident-report.png)

Once submitted, the user is presented with all of the incident resources they need to start managing the incident.

![](../.gitbook/assets/admin-ui-incident-report-receipt.png)

![](../.gitbook/assets/admin-ui-incident-report-resources.png)

## During

After an incident is created, Dispatch will engage new participants automatically. Which participants are engaged is determined by rules defined in the Dispatch Admin UI.

Each new participant receives a welcome message \(Email + Slack\) providing them resources and information to orient them for this given incident.

![Incident welcome email](../.gitbook/assets/email-incident-welcome.png)

![Incident welcome slack (ephemeral)](https://lh4.googleusercontent.com/EgiaPr7p7X-MsmhU7LCNn9BoM0qgqlj-yFBRsxHYGFY6GWSVmYkqNjDzFB-iTNpZBlaxjpVJ_R8HC5jO9gu12ehtIGfT3-7At7lQms-dppkxiFZTyOA8LUQyubCDqLAU23NYwcoQfrw)

Throughout the incident, Dispatch manages the resources necessary to run your investigation, while also providing reminders and notifications.

## After

After an incident is marked stable, Dispatch continues to help with incident management creating additional resources such as Post Incident Review \(PIRs\) documents.

## Notifications

In addition to Dispatch engaging individuals that will be directly responsible for managing the incident, it provides notifications for general awareness throughout the organization.

{% hint style="info" %}
The new incident notification message includes a "Join Incident" button; this allows individuals to add themselves to the incident \(and its resources\) without involvement from the incident commander.
{% endhint %}

## Self-service engagement

Often participants will want to "self-subscribe" to incidents given a set of parameters. Dispatch allows individuals to be automatically engaged given these parameters.

To set up an individual's engagement, navigate to `Contact > Individual` and either edit an existing individual or create a new one.

Next, modify the individual's engagement by selecting or adding terms or phrases that you would like to be engaged when found in an incident attributes, inviting the user when a match is found.

For more documentation of incident engagement see [here](administration/contacts.md).

### How it works

For any given set of parameters (incident type, incident priority, title, description, etc.) Dispatch will attempt to engage any individual that has associated with those parameters. Currently, this is an "OR" association between terms. Meaning that if any term is matched, the individual will be pulled into the incident.

As the incident evolves, new information is uncovered. Dispatch will re-evaluate these associations any time those parameters change, adding additional individuals if necessary.

As an example, take an incident that is reported as a "Credential Leak". Dispatch will engage any individual that has associated the terms "Credential", "Leak", and "Credential Leak" (case and punctuation are ignored).

Now, if we find out during the investigation that the incident is really a "System Compromise" and we change the description and title appropriately, Dispatch will then pull in individuals associated with the terms "System", "Compromise", and "System Compromise".
