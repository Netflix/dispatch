import { AuthPage } from "../pages/auth-page"
import { generateRandomString } from "./common"

async function register(authPage: AuthPage): Promise<void> {
  let email = generateRandomString() + "@example.com"
  let password = generateRandomString()
  await authPage.registerNewUser(email, password)
}

export default register
