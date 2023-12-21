const fs = require("fs")
const dotenv = require("dotenv")
const packageJson = require("./package.json")

// Load environment variables from .env file
dotenv.config()

if (
  process.env.FORMKIT_ENTERPRISE_TOKEN &&
  process.env.FORMKIT_ENTERPRISE_TOKEN.startsWith("npm_")
) {
  console.log("Adding @formkit/pro to package.json")
  packageJson.dependencies["@formkit/pro"] = "npm:@formkit-enterprise/pro@^0.119.2"
  fs.writeFileSync("./package.json", JSON.stringify(packageJson, null, 2))
}
