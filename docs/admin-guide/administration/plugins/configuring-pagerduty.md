---
description: Configuration options for the PagerDuty plugin.
---

# Configuring PagerDuty

{% hint style="info" %}
Dispatch ships with support for resolving on-call schedules via the PagerDuty API.
{% endhint %}

### Env Configuration

Add the following env vars to your `.env` file.

## `PAGERDUTY_API_KEY` \[Required. Secret: True\]

> PagerDuty API key.

## `PAGERDUTY_API_FROM_EMAIL` \[Required\]

> Email to be added to all outgoing incident pages.

## Oncall Service Configuration

Go to /services on your Web server running Dispatch and add a new service. Select type `pagerduty-oncall` and add your PagerDuty Service ID in the external id field.

![](../../../../.gitbook/assets/pagerduty-service-setup.png)
