<template>
  <v-menu v-model="menu" :close-on-content-click="false">
    <template #activator="{ props }">
      <v-text-field
        v-model="windowText"
        :label="label"
        v-bind="props"
        append-icon="mdi-calendar"
        hint="Format: yyyy-mm-dd ~ yyyy-mm-dd"
        clearable
        :rules="dateRules"
        @click:clear="clearWindow"
      />
    </template>
    <v-card>
      <v-container>
        <v-row>
          <v-col>
            <v-list>
              <v-list-item v-for="(item, index) in windows" :key="index" @click="setWindow(item)">
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
          <v-col>
            <v-date-picker title="Start Date" v-model="start" show-adjacent-months />
          </v-col>
          <v-col>
            <v-date-picker title="End Date" v-model="end" show-adjacent-months />
          </v-col>
        </v-row>
      </v-container>
      <v-card-actions class="justify-end">
        <v-btn color="info" variant="text" @click="menu = false"> Ok </v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script>
import endOfYear from "date-fns/endOfYear"
import startOfMonth from "date-fns/startOfMonth"
import startOfYear from "date-fns/startOfYear"
import subDays from "date-fns/subDays"
import subMonths from "date-fns/subMonths"
import subYears from "date-fns/subYears"
import { format, endOfQuarter, startOfQuarter, subQuarters } from "date-fns"

let today = function () {
  return new Date()
}

const DATE_FORMAT = "yyyy-MM-dd"

function convertStringToDate(value) {
  let parts = value.split("-")
  let year = parseInt(parts[0], 10)
  let month = parseInt(parts[1], 10) - 1
  let day = parseInt(parts[2], 10)

  return new Date(year, month, day)
}

export default {
  name: "DateWindowInput",
  inheritAttrs: false,
  props: {
    modelValue: {
      type: Object,
      default: function () {
        return { start: null, end: null }
      },
      required: true,
    },
    label: {
      type: String,
      default: "Reported At",
    },
  },

  data() {
    return {
      menu: false,
      start: null,
      end: null,
      windowText: null,
      dateRules: [
        (value) =>
          !value ||
          /^(\d{4}-\d{2}-\d{2} ~ \d{4}-\d{2}-\d{2})$/.test(value) ||
          "Invalid date (expected format: yyyy-mm-dd ~ yyyy-mm-dd)",
      ],
      windows: [
        { title: "Today", start: today(), end: today() },
        { title: "Yesterday", start: subDays(today(), 1), end: subDays(today(), 1) },
        { title: "This Month", start: startOfMonth(today()), end: today() },
        {
          title: "This Quarter",
          start: startOfQuarter(today()),
          end: endOfQuarter(today()),
        },
        {
          title: "This Year",
          start: startOfYear(today()),
          end: endOfYear(today()),
        },
        { title: "Last 7 Days", start: subDays(today(), 7), end: today() },
        { title: "Last 30 Days", start: subDays(today(), 30), end: today() },
        { title: "Last 3 Months", start: subMonths(today(), 3), end: today() },
        { title: "Last 12 Months", start: subMonths(today(), 12), end: today() },
        {
          title: "Last Quarter",
          start: startOfQuarter(subQuarters(today(), 1)),
          end: endOfQuarter(subQuarters(today(), 1)),
        },
        {
          title: "Last Year",
          start: startOfYear(subYears(today(), 1)),
          end: endOfYear(subYears(today(), 1)),
        },
      ],
    }
  },

  created() {
    if (this.modelValue.start) {
      this.start = convertStringToDate(this.modelValue.start)
    }
    if (this.modelValue.end) {
      this.end = convertStringToDate(this.modelValue.end)
    }
  },

  watch: {
    windowText: {
      handler(value) {
        if (this.dateRules.every((rule) => rule(value) === true)) {
          if (value) {
            let parts = value.split("~")
            if (parts.length == 2) {
              if (this.formatDate(this.start) !== parts[0]) {
                this.start = this.getDatetime(parts[0])
              }

              if (this.formatDate(this.end) !== parts[1]) {
                this.end = this.getDatetime(parts[1])
              }
            }
          }
        }
      },
    },
    start: {
      handler(value) {
        if (value) {
          this.$emit("update:modelValue", {
            start: this.formatDate(value),
            end: this.formatDate(this.end),
          })
        }
        this.setWindowText()
      },
    },
    end: {
      handler(value) {
        if (value) {
          this.$emit("update:modelValue", {
            start: this.formatDate(this.start),
            end: this.formatDate(value),
          })
        }
        this.setWindowText()
      },
    },
  },

  methods: {
    formatDate: function (value) {
      return format(value, DATE_FORMAT)
    },
    clearWindow: function () {
      this.start = null
      this.end = null
    },
    setWindow: function (item) {
      this.start = item.start
      this.end = item.end
      this.setWindowText()
    },
    getDatetime: function (value) {
      return new Date(value)
    },
    setWindowText: function () {
      let startDate = this.start ? this.formatDate(this.start) : ""
      let endDate = this.end ? this.formatDate(this.end) : ""

      if (startDate && endDate) {
        this.windowText = `${startDate} ~ ${endDate}`
      } else {
        this.windowText = null
      }
    },
  },
}
</script>
