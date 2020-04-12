import axios from "axios"
import router from "@/router"
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
    let path = router.currentRoute.path
    if (err.response.status == 401 && path != "/login" && path != "/register") {
      router.push("/login")
    }
    Promise.reject(err)
    return err
  }
)

export default instance
