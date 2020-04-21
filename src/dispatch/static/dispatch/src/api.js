import axios from "axios"
import store from "@/store"

const instance = axios.create({
  baseURL: "/api/v1"
})

instance.interceptors.request.use(
  config => {
    let token = store.state.account.accessToken
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
    if (err.response.status == 401) {
      store.dispatch("account/logout")
    }
    Promise.reject(err)
    return err
  }
)

export default instance
