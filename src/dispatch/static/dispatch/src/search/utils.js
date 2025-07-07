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
  createFastAPIFilterParameters(options, model) {
    let [sortBy, descending] = this.createSortExpression(options.sortBy, options.descending)
    let params = this.createFastAPIFilterParams(options.filters)
    
    // Remove filters from options to avoid duplication
    let cleanOptions = { ...options }
    delete cleanOptions.filters
    delete cleanOptions.sortBy
    delete cleanOptions.descending
    
    // Add sorting parameters
    if (sortBy && sortBy.length > 0) {
      params.order_by = descending[0] ? `-${sortBy[0]}` : sortBy[0]
    }
    
    return {
      ...cleanOptions,
      ...params
    }
  },
  
  createFastAPIFilterParams(filters) {
    let params = {}
    
    forEach(filters, function (value, key) {
      // Handle date ranges
      if (has(value, "start") && value.start) {
        params[`${key}__gte`] = value.start
        if (value.end) {
          params[`${key}__lte`] = value.end
        }
      } 
      // Handle arrays of objects (like case types, priorities, etc.)
      else if (Array.isArray(value) && value.length > 0) {
        // Filter out null/undefined values
        let validValues = value.filter(v => v !== null && v !== undefined)
        
        if (validValues.length > 0) {
          if (key === "assignee" || key === "participant") {
            // Handle participant/assignee specially - map to email
            let emails = validValues.map(v => v.email || (v.individual && v.individual.email)).filter(Boolean)
            if (emails.length > 0) {
              params[`${key === "assignee" ? "assignee_email" : "reporter_email"}__in`] = emails
            }
          } else if (key === "case_type" || key === "case_priority" || key === "case_severity") {
            // Map object arrays to ID arrays
            let ids = validValues.map(v => v.id).filter(Boolean)
            if (ids.length > 0) {
              params[`${key}_id__in`] = ids
            }
          } else if (key === "project") {
            // Map project objects to ID arrays
            let ids = validValues.map(v => v.id).filter(Boolean)
            if (ids.length > 0) {
              params["project_id__in"] = ids
            }
          } else if (key === "tag") {
            // Map tag objects to ID arrays
            let ids = validValues.map(v => v.id).filter(Boolean)
            if (ids.length > 0) {
              params["tag_id__in"] = ids
            }
          } else if (key === "tag_type") {
            // Map tag type objects to ID arrays
            let ids = validValues.map(v => v.id).filter(Boolean)
            if (ids.length > 0) {
              params["tag_type_id__in"] = ids
            }
          } else if (key === "status") {
            // Status is already an array of strings
            params["status__in"] = validValues
          } else {
            // Default case - assume it's an array of values
            params[`${key}__in`] = validValues
          }
        }
      }
      // Handle single values
      else if (value !== null && value !== undefined && !Array.isArray(value) && !has(value, "start")) {
        params[key] = value
      }
    })
    
    return params
  },
  
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
    let [sortBy, descending] = this.createSortExpression(options.sortBy, options.descending)
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
          // filter null/undefined values but allow false
          if (value === null || value === undefined) {
            return
          }
          if (["commander", "participant", "assignee"].includes(key) && has(value, "email")) {
            subFilter.push({
              model: toPascalCase(key),
              field: "email",
              op: "==",
              value: value.email,
            })
          } else if (["commander", "participant", "assignee"].includes(key)) {
            subFilter.push({
              model: toPascalCase(key),
              field: "email",
              op: "==",
              value: value.individual.email,
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
            // avoid filter null/undefined values but allow false
            if (value.value !== null && value.value !== undefined) {
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
