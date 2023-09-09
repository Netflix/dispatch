import { parseISO, formatISO } from "date-fns"
import moment from "moment-timezone"

const time_format = "YYYY-MM-DD HH:mm:ss"
const zones_to_show = ["America/Los_Angeles", "America/New_York"]

export function formatHash(value) {
  if (value) {
    return value.slice(0, 7)
  }
}

export function formatDate(value) {
  if (value) {
    return formatISO(parseISO(value))
  }
}

export function formatToUTC(value) {
  if (value) {
    return moment(value).utc().format(time_format)
  }
}

function formatTimeZone(time) {
  return `${time.format("z")}: ${time.format(time_format)}`
}

export function formatToTimeZones(value) {
  if (value) {
    const m = moment(value)
    if (!m.isValid()) return value
    const local_zone_name = moment.tz.guess() || "America/Los_Angeles"
    const local_time = m.tz(local_zone_name)
    let tooltip_text = `${formatTimeZone(local_time)}`
    zones_to_show.forEach((zone) => {
      if (zone != local_zone_name) {
        const zoned_time = m.tz(zone)
        tooltip_text += `\n${formatTimeZone(zoned_time)}`
      }
    })
    return tooltip_text
  }
}

export function formatRelativeDate(value) {
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
}

export function initials(value) {
  if (value) {
    return value
      .split(" ")
      .map((n) => n[0])
      .slice(0, 2)
      .join("")
  }
}

export function asString(value) {
  if (!value) return ""
  return value.toString()
}

export function capitalize(value) {
  if (!value) return ""
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function toUSD(value) {
  if (value) {
    var formatter = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumSignificantDigits: 6,
    })
    return formatter.format(value)
  }
  return value
}

export function toNumberString(value) {
  if (value) {
    var formatter = new Intl.NumberFormat("en-US", {
      maximumSignificantDigits: 6,
    })
    return formatter.format(value)
  }
  return value
}

export function deslug(value) {
  if (value) {
    return value
      .split("-")
      .slice(2)
      .map(function (word) {
        return word.charAt(0).toUpperCase() + word.slice(1)
      })
      .join(" ")
  }
}

export function snakeToCamel(value) {
  if (value) {
    return value
      .split("_")
      .map(function (value) {
        return value.charAt(0).toUpperCase() + value.substring(1)
      })
      .join(" ")
  }
}

export function commaString(value, key) {
  if (value) {
    return value
      .map(function (el) {
        return el[key]
      })
      .join(", ")
  }
}

export function activeRoles(value) {
  if (value) {
    let active_roles = value
      .filter((role) => !role.renounced_at)
      .map(function (role) {
        return role.role
      })
      .join(", ")
    if (active_roles) {
      return active_roles
    } else {
      return "Inactive"
    }
  }
}

export function individualNames(value) {
  if (value) {
    return value
      .map(function (item) {
        return item.individual.name
      })
      .join(", ")
  }
}
