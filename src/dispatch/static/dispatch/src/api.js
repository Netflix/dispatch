import axios from "axios"
import store from "@/store"
import router from "./router"

const instance = axios.create({
  baseURL: "/api/v1"
})

const authProviderSlug = process.env.VUE_APP_DISPATCH_AUTHENTICATION_PROVIDER_SLUG

instance.interceptors.request.use(
  config => {
    let token = store.state.auth.accessToken
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`
    }

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  function(res) {
    return res
  },
  function(err) {
    // TODO account for other auth providers

    if (err.response.status == 401) {
      if (authProviderSlug === "dispatch-auth-provider-basic") {
        router.push({ path: "/login" })
      }
    }
    if (err.response.status == 500) {
      store.commit(
        "app/SET_SNACKBAR",
        {
          text:
            "Something has gone very wrong, please retry or let your admin know that you received this error.",
          color: "red"
        },
        { root: true }
      )
    }
    return Promise.reject(err)
  }
)

export default instance
