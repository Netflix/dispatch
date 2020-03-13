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
      currency: "USD"
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
