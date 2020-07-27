// src/service-worker.js

// If you are using 'GenerateSW' (default) for your workboxPluginMode setting this file is auto generated for you.
// If you are using 'InjectManifest' then add this to your custom SW after your standard workbox config

self.addEventListener("message", event => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting()
  }
})
