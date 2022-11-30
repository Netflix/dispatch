import axios from "axios"
import store from "@/store"
import auth_store from "@/auth/store"

import router from "./router"

const instance = axios.create({
  baseURL: "/api/v1",
})

const authProviderSlug =
  import.meta.env.VITE_DISPATCH_AUTHENTICATION_PROVIDER_SLUG || "dispatch-auth-provider-basic"

instance.interceptors.request.use(
  (config) => {
    // we don't want to send null/empty values to the API
    // TODO do we need to do this for all params?
    if (config.params) {
      if (!config.params["q"]) {
        delete config.params["q"]
      }
    }
    let token = auth_store.state.currentUser.token
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

instance.interceptors.request.use(function (config) {
  if (!config.url.includes("organization")) {
    let currentOrganization = store.state.route.params.organization || null

    if (currentOrganization) {
      config.url = `${currentOrganization}${config.url}`
    }
  }
  return config
})

instance.interceptors.response.use(
  function (res) {
    return res
  },
  function (err) {
    if (err.response) {
      if (err.response.status == 401) {
        if (authProviderSlug === "dispatch-auth-provider-basic") {
          router.push({ name: "BasicLogin" })
        } else {
          router.go()
        }
      }

      // allow us to turn off error handling where necessary
      if (
        Object.prototype.hasOwnProperty.call(err.config, "errorHandle") &&
        err.config.errorHandle === false
      ) {
        return Promise.reject(err)
      }

      if (err.response.status == 403) {
        let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
        store.commit(
          "notification_backend/addBeNotification",
          {
            text: errorText,
            type: "error",
          },
          { root: true }
        )
      }

      if (err.response.status == 409) {
        let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
        store.commit(
          "notification_backend/addBeNotification",
          {
            text: errorText,
            type: "error",
          },
          { root: true }
        )
      }

      if (err.response.status == 422) {
        let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
        store.commit(
          "notification_backend/addBeNotification",
          {
            text: errorText,
            type: "error",
          },
          { root: true }
        )
      }

      if (err.response.status == 500) {
        let errorText = err.response.data.detail.map(({ msg }) => msg).join(" ")
        if (errorText.length == 0) {
          errorText =
            "Something has gone wrong, please retry or let your admin know that you received this error."
        }
        store.commit(
          "notification_backend/addBeNotification",
          {
            text: errorText,
            type: "error",
          },
          { root: true }
        )
      }
      return Promise.reject(err)
    }
  }
)

export default instance
