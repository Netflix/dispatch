<template>
  <v-menu
    ref="menu"
    v-model="display"
    :close-on-content-click="false"
    :nudge-right="40"
    transition="scale-transition"
    offset-y
    max-width="290px"
    min-width="290px"
  >
    <template v-slot:activator="{ on }">
      <v-text-field
        v-model="datetime"
        label="Select Datetime"
        prepend-icon="event"
        readonly
        v-on="on"
      />
    </template>
    <v-card>
      <v-card-text class="px-0 py-0">
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
            <v-date-picker v-model="date" @input="showTimePicker" full-width></v-date-picker>
          </v-tab-item>
          <v-tab-item key="timer">
            <v-time-picker v-model="time" full-width></v-time-picker>
          </v-tab-item>
        </v-tabs>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <slot name="actions" :parent="this">
          <v-btn color="grey lighten-1" text @click.native="clearHandler">Clear</v-btn>
          <v-btn text @click="okHandler">Ok</v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>
<script>
import { parse } from "date-fns"
import { format, utcToZonedTime } from "date-fns-tz"

const DEFAULT_DATE = ""
const DEFAULT_TIME = "00:00:00"
const DEFAULT_DATE_FORMAT = "yyyy-MM-dd"
const DEFAULT_TIME_FORMAT = "HH:mm:ss"

export default {
  name: "DatetimeTimePickerMenu",

  model: {
    prop: "datetime",
    event: "input",
  },

  props: {
    datetime: {
      type: [Date, String],
      default: null,
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
        // see https://stackoverflow.com/a/9436948
        initDateTime = parse(this.datetime, this.dateTimeFormat, new Date())
      }
      // localtimezone
      let timezone = new Date().getTimezoneOffset()
      let localDatetime = utcToZonedTime(initDateTime, timezone)
      this.date = format(localDatetime, DEFAULT_DATE_FORMAT)
      this.time = format(localDatetime, DEFAULT_TIME_FORMAT)
    },
    okHandler() {
      this.resetPicker()
      const formatInTimeZone = (date, fmt, tz) =>
        format(utcToZonedTime(date, tz), fmt, { timeZone: tz })
      const formattedTime = formatInTimeZone(this.selectedDatetime, "yyyy-MM-dd'T'HH:mmXXX", "UTC")

      this.$emit("input", formattedTime)
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
