import jsonpath from "jsonpath"
import json_to_ast from "json-to-ast"

/**
 * Finds the path to a key in an object hierarchy.
 *
 * @param obj - The object to search in.
 * @param key - The key to find.
 * @param value - The value of the key to find.
 * @param path - The current path (for internal use).
 * @returns The path to the key as a string if found, otherwise null.
 *
 * @example
 *
 * const obj = {
 *   a: {
 *     b: {
 *       c: 'value'
 *     }
 *   }
 * };
 * const path = findPath(obj, 'c', 'value'); // Returns '$.a.b.c'
 */
export function findPath<T>(obj: T, key: keyof any, value: any, path: string = "$"): string | null {
  if (Array.isArray(obj)) {
    for (let i = 0; i < obj.length; i++) {
      const arrayPath = `${path}[${i}]`
      const result = findPath(obj[i], key, value, arrayPath)
      if (result) return result
    }
  } else if (typeof obj === "object" && obj !== null) {
    for (const [k, v] of Object.entries(obj)) {
      // Check if key contains special characters (non-alphanumeric or underscore)
      const currentPath = /\W/.test(k) ? `${path}['${k}']` : `${path}.${k}`
      if (k === key && simpleDeepEqual(v, value)) return currentPath
      if (typeof v === "object") {
        const result = findPath(v, key, value, currentPath)
        if (result) return result
      }
    }
  }
  return null
}

// Using JSON.stringify for deep equality check
function simpleDeepEqual(a: any, b: any): boolean {
  try {
    return JSON.stringify(a) === JSON.stringify(b)
  } catch {
    return false
  }
}

/**
 * Extracts a key-value pair from a string line of JSON.
 *
 * @param lineContent - The string to extract from.
 * @returns An object with key and value properties.
 *
 * @example
 *
 * const lineContent = '"key": "value",';
 * const { key, value } = extractKeyValueRegex(lineContent); // Returns { key: 'key', value: 'value' }
 */
export function extractKeyValue(lineContent: string): { key: string; value: any } {
  // Remove trailing comma if it exists to make it a valid JSON object
  const trimmedLine = lineContent.trim().replace(/,\s*$/, "")
  // Add curly braces to make it a valid JSON string
  const jsonString = `{${trimmedLine}}`

  try {
    // Parse the JSON string
    const parsed = JSON.parse(jsonString)

    // Extract the first key-value pair
    const key = Object.keys(parsed)[0]
    const value = parsed[key]

    // Return the extracted key and the value as a string
    return { key, value }
  } catch (error) {
    console.error(`Error parsing lineContent: ${lineContent}`, error)
    return { key: null, value: null }
  }
}

/**
 * Finds the start and end positions of a JSONPath within a JSON string.
 *
 * @param json - The JSON string to search in.
 * @param targetJPath - The JSONPath to find the positions of.
 * @returns An array of objects, where each object represents one occurrence of the JSONPath and contains the start and end positions.
 *
 * @example
 *
 * const json = `{
 *   "a": {
 *     "b": {
 *       "c": "value"
 *     },
 *     "d": {
 *       "c": "another value"
 *     }
 *   }
 * }`;
 * const positions = findPositions(json, '$..c');
 * // Returns [{ start: 21, end: 30 }, { start: 51, end: 67 }]
 */
export function findPositions(json: string, targetJPath: string) {
  const positions = []
  const parsedJson = JSON.parse(json)

  // Use jsonpath to find all matching paths
  const paths = jsonpath.paths(parsedJson, targetJPath)

  for (const path of paths) {
    const value = JSON.stringify(jsonpath.value(parsedJson, jsonpath.stringify(path)))

    const start = json.indexOf(value)
    const end = start + value.length
    positions.push({ start, end })
  }

  return positions
}
