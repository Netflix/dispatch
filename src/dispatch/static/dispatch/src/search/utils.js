import { forEach, each, has } from "lodash"

const toPascalCase = (str) =>
  `${str}`
    .replace(new RegExp(/[-_]+/, "g"), " ")
    .replace(new RegExp(/[^\w\s]/, "g"), "")
    .replace(
      new RegExp(/\s+(.)(\w+)/, "g"),
      ($1, $2, $3) => `${$2.toUpperCase() + $3.toLowerCase()}`
    )
    .replace(new RegExp(/\s/, "g"), "")
    .replace(new RegExp(/\w/), (s) => s.toUpperCase())

export default {
  mapQueryParamsToTableOptions(options, queryParams) {
    forEach(queryParams, function (values, key) {
      if (Array.isArray(values)) {
        each(values, function (value) {
          options[key].push({ name: value })
        })
      } else {
        options[key].push({ name: values })
      }
    })
  },
  mapTableOptionsToQueryParams(options, queryParams) {
    return options, queryParams
  },
  createParametersFromTableOptions(options, model, rawFilters) {
    let expression = this.createFilterExpression(options.filters, model)
    delete options.filters

    if (!expression.length) {
      if (rawFilters != null && typeof rawFilters[Symbol.iterator] === "function") {
        expression = { and: [...rawFilters] }
        return { ...options, filter: JSON.stringify(expression) }
      } else {
        return options
      }
    }

    if (rawFilters != null && typeof rawFilters[Symbol.iterator] === "function") {
      expression = { and: [...rawFilters, ...expression] }
    } else {
      expression = { and: expression }
    }

    return { ...options, filter: JSON.stringify(expression) }
  },
  createFilterExpression(filters, model) {
    let filterExpression = []
    forEach(filters, function (value, key) {
      let subFilter = []
      // Handle time windows
      if (has(value, "start")) {
        if (value.start) {
          subFilter.push({
            and: [
              { model: model, field: key, op: ">=", value: value.start },
              { model: model, field: key, op: "<=", value: value.end },
            ],
          })
        }
      } else {
        each(value, function (value) {
          // filter null values
          if (!value) {
            return
          }
          if (has(value, "id")) {
            subFilter.push({
              model: toPascalCase(key),
              field: "id",
              op: "==",
              value: value.id,
            })
          } else if (has(value, "name")) {
            subFilter.push({
              model: toPascalCase(key),
              field: "name",
              op: "==",
              value: value.name,
            })
          } else if (has(value, "model")) {
            // avoid filter null values
            if (value.value) {
              subFilter.push({
                model: value.model,
                field: value.field,
                op: "==",
                value: value.value,
              })
            }
          } else {
            subFilter.push({ model: model, field: key, op: "==", value: value })
          }
        })
      }
      if (subFilter.length > 0) {
        filterExpression.push({ or: subFilter })
      }
    })

    return filterExpression
  },
}
