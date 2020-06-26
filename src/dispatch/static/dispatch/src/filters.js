import Vue from "vue"
import moment from "moment"

Vue.filter("formatDate", function(value) {
  if (value) {
    return moment
      .utc(String(value))
      .local()
      .calendar()
  }
})

Vue.filter("asString", function(value) {
  if (!value) return ""
  return value.toString()
})

Vue.filter("capitalize", function(value) {
  if (!value) return ""
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
})

Vue.filter("toUSD", function(value) {
  if (value) {
    var formatter = new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumSignificantDigits: 6
    })
    return formatter.format(value)
  }
  return value
})

Vue.filter("toNumberString", function(value) {
  if (value) {
    var formatter = new Intl.NumberFormat("en-US", {
      maximumSignificantDigits: 6
    })
    return formatter.format(value)
  }
  return value
})

Vue.filter("deslug", function(value) {
  if (value) {
    return value
      .split("-")
      .slice(2)
      .map(function(word) {
        return word.charAt(0).toUpperCase() + word.slice(1)
      })
      .join(" ")
  }
})

Vue.filter("snakeToCamel", function(value) {
  if (value) {
    return value
      .split("_")
      .map(function(value) {
        return value.charAt(0).toUpperCase() + value.substring(1)
      })
      .join(" ")
  }
})

Vue.filter("commaString", function(value, key) {
  if (value) {
    return value
      .map(function(el) {
        return el[key]
      })
      .join(", ")
  }
})
