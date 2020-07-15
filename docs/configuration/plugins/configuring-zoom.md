---
description: Configuration options for the Zoom plugin.
---

# Configuring Zoom

{% hint style="info" %}
Dispatch ships with Zoom conference support. The Zoom plugin creates a conference call with a valid time of 6 weeks and generates a password to protect the call. The Web URL returned by the plugin to the messaging is created such that you just need to click it and not worry about entering the password. This plugin is not required for core functionality, however a plugin of type `conference` must always be enabled.
{% endhint %}

## `ZOOM_API_USER_ID` \[Required. Secret: True\]

> Email / User ID attached to the JWT credentials.

## `ZOOM_API_KEY` \[Required\]

> JWT API Key.

## `ZOOM_API_SECRET` \[Required. Secret: True\]

> JWT API Secret.

## Create the Zoom Application for your API Keys

To create the API Keys required for the Zoom plugin, navigate to the Zoom Marketplace and [create an App](https://marketplace.zoom.us/develop/create). Make sure you are logged in as the user that you wish to tie the API credentials to.

Create a `JWT` application to generate the JWT API Key and Secret. Make sure to set the `Intent to publish: No`.

