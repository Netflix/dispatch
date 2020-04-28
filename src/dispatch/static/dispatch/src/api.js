import axios from "axios"
import store from "@/store"
import router from "./router"

const instance = axios.create({
  baseURL: "/api/v1"
})

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
      router.push({ path: "/login" })
    }
    return Promise.reject(err)
  }
)

export default instance
