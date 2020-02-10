const jsf = require("json-schema-faker")
jsf.extend("faker", function() {
  return require("faker")
})

const schema = require("./schema")
const fs = require("fs")

const json = JSON.stringify(jsf(schema))

fs.writeFile("./mock/db.json", json, function(err) {
  if (err) {
    return console.log(err)
  } else {
    console.log("mock data created.")
  }
})
