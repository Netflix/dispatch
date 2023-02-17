export function isValidRegex(pattern) {
  try {
    new RegExp(pattern)
    return true
  } catch (e) {
    return false
  }
}
