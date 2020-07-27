---
description: Configuration options for the PagerDuty plugin.
---

# Configuring PagerDuty

{% hint style="info" %}
Dispatch ships with support for resolving oncall schedules via the PagerDuty API. Below, is how to configure the PagerDuty plugin to work with `Dispatch`. This plugin is not required for core functionality, however a plugin of type `oncall` must always be enabled.
{% endhint %}

## `PAGERDUTY_API_KEY` \[Required. Secret: True\]

> PagerDuty API key.

## `PAGERDUTY_API_FROM_EMAIL` \[Required\]

> Email to be added to all outgoing incident pages.

