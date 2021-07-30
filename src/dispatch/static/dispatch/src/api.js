import axios from "axios"
import store from "@/store"
import auth_store from "@/auth/store"

import router from "./router"

const instance = axios.create({
  baseURL: "/api/v1",
})

const authProviderSlug =
  process.env.VUE_APP_DISPATCH_AUTHENTICATION_PROVIDER_SLUG || "dispatch-auth-provider-basic"

instance.interceptors.request.use(
  (config) => {
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

// we don't want to send null/empty values to the API
// TODO do we need to do this for all params?
instance.interceptors.request.use(
  (config) => {
    if (!config.params["q"]) {
      delete config.params["q"]
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
          store.dispatch("auth/logout")
        }
      }

      // allow us to turn off error handling where necessary
      if (error.config.hasOwnProperty("errorHandle") && error.config.errorHandle === false) {
        return Promise.reject(error)
      }
      if (err.response.status == 422) {
        let errorText = err.response.data.detail[0].msg
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
        store.commit(
          "notification_backend/addBeNotification",
          {
            text: "Something has gone wrong, please retry or let your admin know that you received this error.",
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
