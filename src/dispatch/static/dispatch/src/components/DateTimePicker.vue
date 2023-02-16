<template>
  <v-card flat>
    <v-card-text>
      <v-tabs fixed-tabs v-model="activeTab">
        <v-tab key="calendar">
          <slot name="dateIcon">
            <v-icon>event</v-icon>
          </slot>
        </v-tab>
        <v-tab key="timer" :disabled="dateSelected">
          <slot name="timeIcon">
            <v-icon>access_time</v-icon>
          </slot>
        </v-tab>
        <v-tab-item key="calendar">
          <v-date-picker v-model="date" @input="showTimePicker"></v-date-picker>
        </v-tab-item>
        <v-tab-item key="timer">
          <v-time-picker v-model="time"></v-time-picker>
        </v-tab-item>
      </v-tabs>
    </v-card-text>
  </v-card>
</template>
<script>
import { parse, parseISO } from "date-fns"
import { format } from "date-fns-tz"

const DEFAULT_DATE = ""
const DEFAULT_TIME = "00:00:00"
const DEFAULT_DATE_FORMAT = "yyyy-MM-dd"
const DEFAULT_TIME_FORMAT = "HH:mm:ss"

export default {
  name: "DatetimeTimePicker",

  model: {
    prop: "datetime",
    event: "input",
  },

  props: {
    datetime: {
      type: [Date, String],
      default: null,
    },
    label: {
      type: String,
      default: "",
    },
    dateFormat: {
      type: String,
      default: DEFAULT_DATE_FORMAT,
    },
    timeFormat: {
      type: String,
      default: "HH:mm",
    },
  },

  data() {
    return {
      display: false,
      activeTab: 0,
      date: DEFAULT_DATE,
      time: DEFAULT_TIME,
    }
  },
  mounted() {
    this.init()
  },

  computed: {
    dateTimeFormat() {
      return this.dateFormat + " " + this.timeFormat
    },
    defaultDateTimeFormat() {
      return DEFAULT_DATE_FORMAT + " " + DEFAULT_TIME_FORMAT
    },
    formattedDatetime() {
      return this.selectedDatetime ? format(this.selectedDatetime, this.dateTimeFormat) : ""
    },
    selectedDatetime() {
      if (this.date && this.time) {
        let datetimeString = this.date + " " + this.time
        if (this.time.length === 5) {
          datetimeString += ":00"
        }
        return parse(datetimeString, this.defaultDateTimeFormat, new Date())
      } else {
        return null
      }
    },
    dateSelected() {
      return !this.date
    },
  },
  methods: {
    init() {
      if (!this.datetime) {
        return
      }
      let initDateTime

      if (this.datetime instanceof Date) {
        initDateTime = this.datetime
      } else if (typeof this.datetime === "string" || this.datetime instanceof String) {
        initDateTime = parseISO(this.datetime)
      }
      this.date = format(initDateTime, DEFAULT_DATE_FORMAT)
      this.time = format(initDateTime, DEFAULT_TIME_FORMAT)
    },
    okHandler() {
      this.resetPicker()
      let isoString = this.selectedDatetime.toISOString()
      this.$emit("input", isoString)
    },
    clearHandler() {
      this.resetPicker()
      this.date = DEFAULT_DATE
      this.time = DEFAULT_TIME
      this.$emit("input", null)
    },
    resetPicker() {
      this.display = false
      this.activeTab = 0
      if (this.$refs.timer) {
        this.$refs.timer.selectingHour = true
      }
    },
    showTimePicker() {
      this.activeTab = 1
    },
  },
  watch: {
    datetime: function () {
      this.init()
    },
  },
}
</script>
