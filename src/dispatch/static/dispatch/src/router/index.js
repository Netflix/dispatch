import Vue from "vue"
import Router from "vue-router"
import { publicRoute, protectedRoute } from "./config"
import NProgress from "nprogress"
import "nprogress/nprogress.css"

import env from "good-env"

import { BasicQueryStringUtils } from "@openid/appauth/built/query_string_utils"
import { LocalStorageBackend } from "@openid/appauth/built/storage"
import { AuthorizationRequest } from "@openid/appauth/built/authorization_request"
import { AuthorizationNotifier } from "@openid/appauth/built/authorization_request_handler"
import { RedirectRequestHandler } from "@openid/appauth/built/redirect_based_handler"
import { AuthorizationServiceConfiguration } from "@openid/appauth/built/authorization_service_configuration"
import { BaseTokenRequestHandler } from "@openid/appauth/built/token_request_handler"
import { GRANT_TYPE_AUTHORIZATION_CODE, TokenRequest } from "@openid/appauth/built/token_request"

import { FetchRequestor } from "@openid/appauth/built/xhr"

import store from "@/store"

const requestor = new FetchRequestor()
const routes = publicRoute.concat(protectedRoute)

const pkce_auth = env.getBool(process.env.VUE_APP_DISPATCH_PKCE_AUTH) || true
const clientId = process.env.VUE_APP_DISPATCH_CLIENT_ID
const openIdConnectUrl = process.env.VUE_APP_DISPATCH_OPEN_ID_CONNECT_URL
const scope = "openid profile email"

Vue.use(Router)

const router = new Router({
  mode: "history",
  linkActiveClass: "active",
  routes: routes
})

const notifier = new AuthorizationNotifier()

const qsUtils = new BasicQueryStringUtils({ useHash: false })
//const origParse = qsUtils.parse
qsUtils.parse = input => {
  return qsUtils.parseQueryString(input.search)
}

const authorizationHandler = new RedirectRequestHandler(new LocalStorageBackend(), qsUtils)
const tokenHandler = new BaseTokenRequestHandler(requestor)

// Get a the openIdConnect configuration
let cfg = null
function getCfg() {
  let rslv, rej
  const resolver = (resolve, reject) => {
    rslv = resolve
    rej = reject
  }

  const p = new Promise(resolver)
  if (cfg === null) {
    AuthorizationServiceConfiguration.fetchFromIssuer(openIdConnectUrl, requestor)
      .then(response => {
        cfg = response
        rslv(cfg)
      })
      .catch(rej)
  } else {
    rslv(cfg)
  }
  return p
}

notifier.setAuthorizationListener((request, response, error) => {
  if (response) {
    let req = new TokenRequest({
      client_id: clientId,
      redirect_uri: request.redirectUri,
      grant_type: GRANT_TYPE_AUTHORIZATION_CODE,
      code: response.code,
      extras: { code_verifier: request.internal["code_verifier"] }
    })
    getCfg().then(cfg => {
      tokenHandler
        .performTokenRequest(cfg, req)
        .then(response => {
          store.dispatch("account/login", {
            token: response.accessToken,
            redirectUri: request.redirectUri
          })
        })
        .catch(e => {
          console.error(e)
        })
    })
  }
})

authorizationHandler.setAuthorizationNotifier(notifier)
// router guards
router.beforeEach((to, from, next) => {
  store.dispatch("app/setLoading", true)

  NProgress.start()
  if (!pkce_auth) {
    next()
  }

  getCfg().then(cfg => {
    if (!store.state.account.status.loggedIn) {
      if (to.query.code && to.query.state) {
        authorizationHandler.completeAuthorizationRequestIfPossible()
      } else if (to.matched.some(record => record.meta.requiresAuth)) {
        // Test if we already have a valid access token
        let redirect_uri = window.location.protocol + "//" + window.location.host + to.path
        const request = new AuthorizationRequest({
          client_id: clientId,
          redirect_uri: redirect_uri,
          scope: scope,
          response_type: AuthorizationRequest.RESPONSE_TYPE_CODE,
          state: undefined,
          extras: {}
        })
        authorizationHandler.performAuthorizationRequest(cfg, request)
      }
    } else {
      next()
    }
  })
})

router.afterEach(function() {
  store.dispatch("app/setLoading", false)

  NProgress.done()
})

export default router
