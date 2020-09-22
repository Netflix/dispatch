---
description: Configuration options for the PagerDuty plugin.
---

# Configuring PagerDuty

{% hint style="info" %}
Dispatch ships with support for resolving oncall schedules via the PagerDuty API. This plugin is not required for core functionality, however a plugin of type `oncall` must always be enabled. The current implementation expects a schedule to be associated with the escalation policy. Below, is how to configure the PagerDuty plugin to work with `Dispatch`.
{% endhint %}

## `PAGERDUTY_API_KEY` \[Required. Secret: True\]

> PagerDuty API key.

## `PAGERDUTY_API_FROM_EMAIL` \[Required\]

> Email to be added to all outgoing incident pages.
