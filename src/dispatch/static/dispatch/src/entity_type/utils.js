import jsonpath from "jsonpath"

export function isValidRegex(pattern) {
  try {
    new RegExp(pattern)
    return true
  } catch (e) {
    return false
  }
}

function sanitizeString(str) {
  return str.replace(/[&<>"'`=/]/g, function (char) {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
      "`": "&#x60;",
      "=": "&#x3D;",
      "/": "&#x2F;",
    }[char]
  })
}

export function isValidJsonPath(jpath) {
  try {
    if (sanitizeString(jpath) !== jpath) {
      return false
    }

    jsonpath.parse(jpath)
    return true
  } catch (e) {
    return false
  }
}
