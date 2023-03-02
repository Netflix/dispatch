import jsonpath from "jsonpath"

export function isValidRegex(pattern) {
  try {
    new RegExp(pattern)
    return true
  } catch (e) {
    return false
  }
}

export function isValidJsonPath(jpath) {
  try {
    jsonpath.parse(jpath)
    return true
  } catch (e) {
    return false
  }
}
