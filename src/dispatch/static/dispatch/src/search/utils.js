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
    let [sortBy, descending] = this.createSortExpression(options.sortBy, model)
    let expression = this.createFilterExpression(options.filters, model)
    delete options.filters
    delete options.sortBy

    if (!expression.length) {
      if (rawFilters != null && typeof rawFilters[Symbol.iterator] === "function") {
        expression = { and: [...rawFilters] }
        return {
          ...options,
          sortBy: sortBy,
          descending: descending,
          filter: JSON.stringify(expression),
        }
      } else {
        return { ...options, sortBy: sortBy, descending: descending }
      }
    }

    if (rawFilters != null && typeof rawFilters[Symbol.iterator] === "function") {
      expression = { and: [...rawFilters, ...expression] }
    } else {
      expression = { and: expression }
    }

    return {
      ...options,
      sortBy: sortBy,
      descending: descending,
      filter: JSON.stringify(expression),
    }
  },
  createSortExpression(sortBy, sortDesc) {
    let descending = []
    each(sortBy, function (sortField, index) {
      descending.push(sortDesc && sortDesc[index] ? true : false)
    })
    return [sortBy, descending]
  },
  /**
   * Create a filter expression for searching for items in a database
   *
   * @param {Object} filters - An object containing the search filters
   * @param {String} model - The name of the model used in the search
   *
   * @return {Array} filterExpression - An array of filter objects that can be used to search the database
   *
   * @example
   * const filters = {
   *   name: "Endpoint infected with Nanocore",
   *   start_date: {
   *     start: "2022-01-01",
   *     end: "2022-12-31"
   *   }
   * }
   * const model = "Case"
   *
   * const filterExpression = createFilterExpression(filters, model)
   * console.log(filterExpression)
   *
   * // Output:
   * // [
   * //   {
   * //     or: [
   * //       {
   * //         model: "Case",
   * //         field: "name",
   * //         op: "==",
   * //         value: "Endpoint infected with Nanocore"
   * //       }
   * //     ]
   * //   },
   * //   {
   * //     and: [
   * //       {
   * //         model: "Case",
   * //         field: "start_date",
   * //         op: ">=",
   * //         value: "2022-01-01"
   * //       },
   * //       {
   * //         model: "Case",
   * //         field: "start_date",
   * //         op: "<=",
   * //         value: "2022-12-31"
   * //       }
   * //     ]
   * //   }
   * // ]
   */
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
          if (["commander", "participant", "assignee"].includes(key) && has(value, "email")) {
            subFilter.push({
              model: toPascalCase(key),
              field: "email",
              op: "==",
              value: value.email,
            })
          } else if (has(value, "id")) {
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
        if (key == "visibility") {
          // use "and" condition to filter with visibility
          filterExpression.push({ and: subFilter })
        } else {
          filterExpression.push({ or: subFilter })
        }
      }
    })

    return filterExpression
  },
}
