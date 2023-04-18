import Vue from "vue"
import { parseISO, formatISO } from "date-fns"

Vue.filter("formatDate", function (value) {
  if (value) {
    return formatISO(parseISO(value))
  }
})

Vue.filter("formatRelativeDate", function (value) {
  if (value) {
    var units = {
      year: 24 * 60 * 60 * 1000 * 365,
      month: (24 * 60 * 60 * 1000 * 365) / 12,
      week: 24 * 60 * 60 * 1000 * 7,
      day: 24 * 60 * 60 * 1000,
      hour: 60 * 60 * 1000,
      minute: 60 * 1000,
      second: 1000,
    }

    const rtf = new Intl.RelativeTimeFormat("en", {
      localeMatcher: "best fit", // other values: "lookup"
      numeric: "always", // other values: "auto"
      style: "long", // other values: "short" or "narrow"
    })
    rtf.format(-1, "day") // "1 day ago"
    rtf.format(-1, "hour") // "1 hour ago"
    rtf.format(-1, "minute") // "1 minute ago"
    rtf.format(-1, "second") // "1 second ago"
    rtf.format(-1, "week") // "1 week ago"
    rtf.format(-1, "month") // "1 month ago"

    var getRelativeTime = (d1, d2 = new Date()) => {
      var elapsed = d1 - d2

      // "Math.abs" accounts for both "past" & "future" scenarios
      for (var u in units)
        if (Math.abs(elapsed) > units[u] || u == "second")
          return rtf.format(Math.round(elapsed / units[u]), u)
    }
    return getRelativeTime(parseISO(value))
  }
})

Vue.filter("initials", function (value) {
  if (value) {
    return value
      .split(" ")
      .map((n) => n[0])
      .slice(0, 2)
      .join("")
  }
})

Vue.filter("asString", function (value) {
  if (!value) return ""
  return value.toString()
})

Vue.filter("capitalize", function (value) {
  if (!value) return ""
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
})

Vue.filter("toUSD", function (value) {
  if (value) {
    var formatter = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumSignificantDigits: 6,
    })
    return formatter.format(value)
  }
  return value
})

Vue.filter("toNumberString", function (value) {
  if (value) {
    var formatter = new Intl.NumberFormat("en-US", {
      maximumSignificantDigits: 6,
    })
    return formatter.format(value)
  }
  return value
})

Vue.filter("deslug", function (value) {
  if (value) {
    return value
      .split("-")
      .slice(2)
      .map(function (word) {
        return word.charAt(0).toUpperCase() + word.slice(1)
      })
      .join(" ")
  }
})

Vue.filter("snakeToCamel", function (value) {
  if (value) {
    return value
      .split("_")
      .map(function (value) {
        return value.charAt(0).toUpperCase() + value.substring(1)
      })
      .join(" ")
  }
})

Vue.filter("commaString", function (value, key) {
  if (value) {
    return value
      .map(function (el) {
        return el[key]
      })
      .join(", ")
  }
})

export const activeRoles = function (value) {
  if (value) {
    return value
      .filter((role) => !role.renounced_at)
      .map(function (role) {
        return role.role
      })
      .join(", ")
  }
}

Vue.filter("activeRoles", activeRoles)

Vue.filter("individualNames", function (value) {
  if (value) {
    return value
      .map(function (item) {
        return item.individual.name
      })
      .join(", ")
  }
})
