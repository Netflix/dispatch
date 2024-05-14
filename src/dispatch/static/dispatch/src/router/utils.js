import { forEach, each, has } from "lodash"

import router from "@/router"

export default {
  serializeFilters(filters) {
    let flatFilters = {}
    forEach(filters, function (value, key) {
      // handle filter windows
      if (has(value, "start")) {
        let startKey = `${key}.start`
        let endKey = `${key}.end`
        flatFilters = { ...flatFilters, ...{ [startKey]: value.start, [endKey]: value.end } }
        return
      }
      each(value, function (item) {
        if (["commander", "participant", "assignee"].includes(key)) {
          if (has(flatFilters, key)) {
            if (typeof item === "string" || item instanceof String) {
              flatFilters[key].push(item)
            } else {
              flatFilters[key].push(item.email)
            }
          } else {
            if (typeof item === "string" || item instanceof String) {
              flatFilters[key] = [item]
            } else {
              flatFilters[key] = [item.email]
            }
          }
        } else {
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
        }
      })
    })
    return flatFilters
  },
  deserializeFilters(query) {
    let filters = {}
    forEach(query, function (value, key) {
      let parts = key.split(".")

      if (parts.length > 1) {
        let root = parts[0]
        if (!filters[root]) {
          filters[root] = { start: null, end: null }
        }

        if (key.includes("start")) {
          filters[root]["start"] = value
        }

        if (key.includes("end")) {
          filters[root]["end"] = value
        }
        return
      }
      if (["status"].includes(key)) {
        if (typeof value === "string" || value instanceof String) {
          if (has(filters, key)) {
            filters[key].push(value)
          } else {
            filters[key] = [value]
          }
        } else {
          each(value, function (item) {
            if (has(filters, key)) {
              filters[key].push(item)
            } else {
              filters[key] = [item]
            }
          })
        }
        return
      }
      if (["commander", "participant", "assignee"].includes(key)) {
        if (typeof value === "string" || value instanceof String) {
          if (has(filters, key)) {
            filters[key].push({ email: value })
          } else {
            filters[key] = [{ email: value }]
          }
        } else {
          each(value, function (item) {
            if (has(filters, key)) {
              filters[key].push({ email: item })
            } else {
              filters[key] = [{ email: item }]
            }
          })
        }
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
