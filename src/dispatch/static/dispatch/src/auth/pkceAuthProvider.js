import { AuthorizationNotifier } from "@openid/appauth/built/authorization_request_handler"
import { AuthorizationRequest } from "@openid/appauth/built/authorization_request"
import { AuthorizationServiceConfiguration } from "@openid/appauth/built/authorization_service_configuration"
import { BaseTokenRequestHandler } from "@openid/appauth/built/token_request_handler"
import { BasicQueryStringUtils } from "@openid/appauth/built/query_string_utils"
import { GRANT_TYPE_AUTHORIZATION_CODE, TokenRequest } from "@openid/appauth/built/token_request"
import { LocalStorageBackend } from "@openid/appauth/built/storage"
import { RedirectRequestHandler } from "@openid/appauth/built/redirect_based_handler"

import { FetchRequestor } from "@openid/appauth/built/xhr"

import store from "@/store"

const requestor = new FetchRequestor()

function login(to, from, next) {
  const clientId = import.meta.env.VITE_DISPATCH_AUTHENTICATION_PROVIDER_PKCE_CLIENT_ID
  const openIdConnectUrl = import.meta.env
    .VITE_DISPATCH_AUTHENTICATION_PROVIDER_PKCE_OPEN_ID_CONNECT_URL
  const scope = "openid profile email"
  const useIdToken = import.meta.env.VITE_DISPATCH_AUTHENTICATION_PROVIDER_USE_ID_TOKEN

  const notifier = new AuthorizationNotifier()

  const qsUtils = new BasicQueryStringUtils({ useHash: false })
  //const origParse = qsUtils.parse
  qsUtils.parse = (input) => {
    return qsUtils.parseQueryString(input.search)
  }

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
        .then((response) => {
          cfg = response
          rslv(cfg)
        })
        .catch(rej)
    } else {
      rslv(cfg)
    }
    return p
  }

  const authorizationHandler = new RedirectRequestHandler(new LocalStorageBackend(), qsUtils)
  authorizationHandler.setAuthorizationNotifier(notifier)

  notifier.setAuthorizationListener((request, response, error) => {
    if (error) {
      console.log(error)
    }
    if (response) {
      let req = new TokenRequest({
        client_id: clientId,
        redirect_uri: request.redirectUri,
        grant_type: GRANT_TYPE_AUTHORIZATION_CODE,
        code: response.code,
        extras: { code_verifier: request.internal["code_verifier"] },
      })
      getCfg().then((cfg) => {
        tokenHandler
          .performTokenRequest(cfg, req)
          .then((response) => {
            // Redirect to the uri in session storage and then delete it from storage
            let token = response.accessToken
            if (useIdToken) {
              token = response.idToken
            }
            store.commit("auth/SET_USER_LOGIN", token)
            store.dispatch("auth/loginRedirect", localStorage.getItem("redirect_uri")).then(() => {
              store.dispatch("auth/createExpirationCheck")
            })
            localStorage.removeItem("redirect_uri")
          })
          .catch((e) => {
            console.error(e)
          })
      })
    }
  })

  getCfg().then((cfg) => {
    if (to.query.code && to.query.state) {
      authorizationHandler.completeAuthorizationRequestIfPossible()
    } else if (to.matched.some((record) => record.meta.requiresAuth)) {
      // Test if we already have a valid access token
      // Set the redirect_uri to a single location and store the real redirect uri in session storage.
      // This enables easier enablement of SPA on providers like Okta where each route must be whitelisted.
      let redirect_uri =
        window.location.protocol + "//" + window.location.host + "/implicit/callback"
      localStorage.setItem(
        "redirect_uri",
        window.location.protocol + "//" + window.location.host + to.fullPath
      )
      const request = new AuthorizationRequest({
        client_id: clientId,
        redirect_uri: redirect_uri,
        scope: scope,
        response_type: AuthorizationRequest.RESPONSE_TYPE_CODE,
        state: undefined,
        extras: {},
      })
      authorizationHandler.performAuthorizationRequest(cfg, request)
    } else {
      next()
    }
  })
}

export default {
  login,
}
