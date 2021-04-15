import { forEach, each, has } from "lodash"

import router from "@/router"

export default {
  serializeFilters(filters) {
    let flatFilters = {}
    forEach(filters, function (value, key) {
      if (key === "window") {
        flatFilters = { ...flatFilters, ...value }
        return
      }
      each(value, function (item) {
        if (has(flatFilters, key)) {
          if (typeof item === "string" || item instanceof String) {
            flatFilters[key].push(item)
          } else {
            flatFilters[key].push(item.name)
          }
        } else {
          if (typeof item === "string" || item instanceof String) {
            flatFilters[key] = [item]
          } else {
            flatFilters[key] = [item.name]
          }
        }
      })
    })
    return flatFilters
  },
  deserializeFilters(query) {
    let filters = {}
    forEach(query, function (value, key) {
      if (["start", "end"].includes(key)) {
        filters.window = { ...filters.window, ...{ [key]: value } }
        return
      }
      if (typeof value === "string" || value instanceof String) {
        if (has(filters, key)) {
          filters[key].push({ name: value })
        } else {
          filters[key] = [{ name: value }]
        }
      } else {
        each(value, function (item) {
          if (has(filters, key)) {
            filters[key].push({ name: item })
          } else {
            filters[key] = [{ name: item }]
          }
        })
      }
    })
    return filters
  },
  updateURLFilters(filters) {
    router.replace({ query: this.serializeFilters(filters) })
  },
}
