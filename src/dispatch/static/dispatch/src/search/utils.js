import { forEach, each, has } from "lodash"

const toPascalCase = str =>
  `${str}`
    .replace(new RegExp(/[-_]+/, "g"), " ")
    .replace(new RegExp(/[^\w\s]/, "g"), "")
    .replace(
      new RegExp(/\s+(.)(\w+)/, "g"),
      ($1, $2, $3) => `${$2.toUpperCase() + $3.toLowerCase()}`
    )
    .replace(new RegExp(/\s/, "g"), "")
    .replace(new RegExp(/\w/), s => s.toUpperCase())

export default {
  createFilterExpression(filters) {
    let filterExpression = []
    forEach(filters, function(value, key) {
      let subFilter = []
      each(value, function(value) {
        if (has(value, "id")) {
          subFilter.push({
            model: toPascalCase(key),
            field: "id",
            op: "==",
            value: value.id
          })
        } else {
          subFilter.push({ field: key, op: "==", value: value })
        }
      })
      if (subFilter.length > 0) {
        filterExpression.push({ or: subFilter })
      }
    })

    if (filterExpression.length > 0) {
      return [{ and: filterExpression }]
    } else {
      return []
    }
  }
}
