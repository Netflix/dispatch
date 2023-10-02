<template>
  <v-menu
    ref="menu"
    v-model="display"
    :close-on-content-click="false"
    max-width="290px"
    min-width="290px"
  >
    <template #activator="{ props }">
      <v-text-field
        v-model="formattedDatetime"
        prepend-icon="mdi-calendar"
        :label="label"
        readonly
        v-bind="props"
      />
    </template>
    <v-card>
      <v-card-text class="px-0 py-0">
        <v-tabs fixed-tabs v-model="activeTab">
          <v-tab key="calendar">
            <slot name="dateIcon">
              <v-icon>mdi-calendar</v-icon>
            </slot>
          </v-tab>
          <v-tab key="timer" :disabled="dateSelected">
            <slot name="timeIcon">
              <v-icon>mdi-clock-outline</v-icon>
            </slot>
          </v-tab>
        </v-tabs>
        <v-window v-model="activeTab">
          <v-window-item key="calendar">
            <v-date-picker v-model="date" @input="showTimePicker" full-width />
          </v-window-item>
          <v-window-item key="timer">
            <v-time-picker v-model="time" full-width />
          </v-window-item>
        </v-window>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <slot name="actions" :parent="this">
          <v-btn color="grey-lighten-1" variant="text" @click="clearHandler">Clear</v-btn>
          <v-btn variant="text" @click="okHandler">Ok</v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>
<script>
import { parse, parseISO } from "date-fns"
import { format } from "date-fns-tz"

const DEFAULT_DATE = ""
const DEFAULT_TIME = "00:00:00"
const DEFAULT_DATE_FORMAT = "yyyy-MM-dd"
const DEFAULT_TIME_FORMAT = "HH:mm:ss"

export default {
  name: "DatetimeTimePickerMenu",

  inheritAttrs: false,

  props: {
    modelValue: {
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
      if (!this.modelValue) {
        return
      }
      let initDateTime

      if (this.modelValue instanceof Date) {
        initDateTime = this.modelValue
      } else if (typeof this.modelValue === "string" || this.datetime instanceof String) {
        initDateTime = parseISO(this.modelValue)
      }
      this.date = format(initDateTime, DEFAULT_DATE_FORMAT)
      this.time = format(initDateTime, DEFAULT_TIME_FORMAT)
    },
    okHandler() {
      this.resetPicker()
      let isoString = this.selectedDatetime.toISOString()
      this.$emit("update:modelValue", isoString)
    },
    clearHandler() {
      this.resetPicker()
      this.date = DEFAULT_DATE
      this.time = DEFAULT_TIME
      this.$emit("update:modelValue", null)
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
    modelValue() {
      this.init()
    },
  },
}
</script>
