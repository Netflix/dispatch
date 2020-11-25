---
description: What to expect as an incident participant.
---

# Incident Participant

## Reporting

Dispatch attempts to make reporting incidents as easy as possible. To that end Dispatch provides a dedicated incident report form that users throughout the organization can submit to engage incident related resources.

Located at: `https://<your-dispatch-domain>/incidents/report`

![](https://lh6.googleusercontent.com/0KWFxWj4SkYVzJw4nviJqm9cmwRZYroJgfJ79PHMDP1WDMFKVwyo9cV4V3Phd6VOub_stA2v0TBRluaN54K85xU6uOhJbe07z2R2ZCzE0JX6AZkLZ35TPjtPd0my07qx_W9LLcO6gZY)

Once submitted the user is then presented with all of the incident resources they need to start managing the incident.

![](https://lh5.googleusercontent.com/WXPlXV3DdOfDY-rL8fBMGeU6O26NauxS3XAFGrWmQvF1THDbmExNcIH_0H40U0ZjyuH_jMiNByHZukbiBbSDx7z3lachOG_X5LO2kmdS2wCMEpWIUZt5VzxnDsrIfWjlq6GYh9SB8bc)

![](https://lh3.googleusercontent.com/Q930J0ZRGeROd9g_15_mMX45CEUp60s__L3efQO2rpH3ZgFAKbmB33O1NOF6IJ3Gr9Xtz2vi1pCb9wfVCWx2pwp_i57bvdI2rsox-YGmTZWz-XsKxIBUlrAVvy3OjgwLUMSF73Jddq4)

## During

After an incident is created Dispatch will start to automatically pull new participants into the incident. Who it pulls is in is determined on rules that have been setup in the Dispatch Admin UI.

Each new participant receives a welcome message \(Email + Slack\) providing them resources and information to help orient them for this given incident.

![Incident welcome email](https://lh3.googleusercontent.com/9AhkQ-y5h-sQN0F6KLrBEE_6cGA-XN4Qu1cj4NAGNj1OOfA7p4c4z0G7BYxydz3oOYCVkqTkl_EYAeO4SOsCWkVXme5hUByCnYNDkFPQhQTkNYulc--rOQNQGD856s4uPZPYHEwvlk0)

![Incident welcome slack (ephemeral)](https://lh4.googleusercontent.com/EgiaPr7p7X-MsmhU7LCNn9BoM0qgqlj-yFBRsxHYGFY6GWSVmYkqNjDzFB-iTNpZBlaxjpVJ_R8HC5jO9gu12ehtIGfT3-7At7lQms-dppkxiFZTyOA8LUQyubCDqLAU23NYwcoQfrw)

From there use the resources as you normally would to run your investigation, Dispatch will be there managing permissions, providing reminders and helping track the incident as it progresses to resolution.

## After

After an incident has been marked stable Dispatch is still there to help creating the resources necessary to run Post Incident Reviews \(PIRs\) and help track any associated action items.

## Notifications

In addition to Dispatch pulling in individuals that will be directly responsible for managing the incident, it provides notifications for general awareness throughout the organization.

{% hint style="info" %}
The incident notification message includes a "Join Incident" button, this allows individuals to add themselves to the incident \(and it's resources\) without involvement from the incident commander.
{% endhint %}

## Self-service engagement

Often participants will want to "self-subscribe" to incidents given a set of parameters. Dispatch allows individuals to be automatically be pulled into an incident given these parameters.

To setup an individual's engagement navigate to Individual and either edit an existing individual or create a new one.

Then under `Engagement` select or add a term or phrase which, when found in an incident you would like to be engaged.

Additionally you can also specify if you would like to be enaged for every incident type or priority.

For more documentation of incident engagement see [here](administration/contacts.md).

### How it works

For any given set of parameters (incident type, incident priority, title, description, etc.) Dispatch will attempt to engage any individual that has associated with those parameters. Current this is an "OR" association between terms. Meaning, that if any term is matched the individual will be pulled into the incident.

As the incident evolves new information is uncovered. Dispatch will re-evaluate these associations any time those parameters change adding additional individuals.

As an example, take an incident that is reported as a "Credential Leak". Dispatch will engage any individual that has associated the terms, "Credential", "Leak" and "Credential Leak" (case and punctuation is ignored).

Now if we find out during investigation that the incident is really a "System Compromise" and we change the description and title appropriately, Dispatch will then pull in individuals associated with the terms "System", "Compromise" and "System Compromise".
