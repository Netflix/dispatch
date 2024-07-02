<template>
  <v-card>
    <v-card-text>
      <div class="mt-3">Edit date/time:</div>
      <v-container fluid class="pa-1">
        <v-row no-gutters class="custom-underline">
          <v-col cols="1" class="pa-0">
            <v-text-field
              v-model="month"
              variant="plain"
              class="m-0"
              density="compact"
              hide-details="true"
              maxlength="2"
              @update:model-value="filterNumeric('month', $event, 'day')"
              @keydown="handleKeyPress('day', $event)"
              @blur="validateMonth"
              @focus="highlightText"
              @click="highlightText"
            />
          </v-col>
          <span class="slash-space">/</span>
          <v-col cols="1" class="pa-0">
            <v-text-field
              v-model="day"
              class="m-0"
              variant="plain"
              density="compact"
              hide-details="true"
              maxlength="2"
              ref="day"
              @update:model-value="filterNumeric('day', $event, 'year')"
              @keydown="handleKeyPress('year', $event)"
              @blur="validateDay"
              @focus="highlightText"
              @click="highlightText"
            />
          </v-col>
          <span class="slash-space">/</span>
          <v-col cols="2" class="pa-0">
            <v-text-field
              v-model="year"
              class="m-0"
              variant="plain"
              density="compact"
              hide-details="true"
              maxlength="4"
              ref="year"
              @update:model-value="filterNumericYear('year', $event, 'hour')"
              @keydown="handleKeyPress('hour', $event)"
              @blur="validateYear"
              @focus="highlightText"
              @click="highlightText"
            />
          </v-col>
          <span class="slash-space">,&nbsp;</span>
          <v-col cols="1" class="pa-0">
            <v-text-field
              v-model="hour"
              class="m-0"
              variant="plain"
              density="compact"
              hide-details="true"
              maxlength="2"
              ref="hour"
              @update:model-value="filterNumeric('hour', $event, 'minutes')"
              @keydown="handleKeyPress('minutes', $event)"
              @blur="validateHour"
              @focus="highlightText"
              @click="highlightText"
            />
          </v-col>
          <span class="colon-space">:</span>
          <v-col cols="1" class="pa-0">
            <v-text-field
              v-model="minutes"
              class="m-0"
              variant="plain"
              density="compact"
              hide-details="true"
              maxlength="2"
              ref="minutes"
              @update:model-value="filterNumeric('minutes', $event, 'seconds')"
              @keydown="handleKeyPress('seconds', $event)"
              @blur="validateMinutes"
              @focus="highlightText"
              @click="highlightText"
            />
          </v-col>
          <span class="colon-space">:</span>
          <v-col cols="3" class="pa-0">
            <v-text-field
              v-model="seconds"
              class="m-0"
              variant="plain"
              density="compact"
              hide-details="true"
              maxlength="6"
              ref="seconds"
              @update:model-value="filterNumericSeconds('seconds', $event)"
              @keydown="handleKeyPress(null, $event, true)"
              @blur="validateSeconds"
              @focus="highlightText"
              @click="highlightText"
            />
          </v-col>
        </v-row>
        <div class="text-caption font-weight-light">{{ timezone || "UTC" }}</div>
      </v-container>
      <div class="mt-3 mb-3">Or paste a Unix timestamp:</div>
      <v-text-field
        class="paste-only"
        v-model="unixTimestamp"
        label="Unix Timestamp"
        readonly
        @paste="handlePaste($event)"
        @focus="highlightText"
        @click="highlightText"
      />
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn variant="text" @click="okHandler">Ok</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { zonedTimeToUtc, utcToZonedTime, format } from "date-fns-tz"
import { fromUnixTime } from "date-fns"

function removeEndingZ(str) {
  if (str.endsWith("Z")) {
    str = str.slice(0, -1)
  }
  return str
}

export default {
  props: {
    modelValue: {
      type: [Date, String],
      default: null,
    },
    timezone: {
      type: String,
      default: null,
    },
  },

  mounted() {
    this.init()
  },

  data() {
    return {
      day: "01",
      month: "01",
      year: "1000",
      hour: "00",
      minutes: "00",
      seconds: "00",
      unixTimestamp: null,
    }
  },
  computed: {
    displayDateTime() {
      if (this.date && this.time !== null && this.seconds !== null) {
        return `${this.date} ${this.time}:${this.seconds}`
      }
      return ""
    },
    dateTimeWithDecimalSeconds() {
      if (this.date && this.time !== null && this.seconds !== null) {
        const [hours, minutes] = this.time.split(":")
        return `${this.date}T${hours}:${minutes}:${this.seconds}`
      }
      return ""
    },
  },
  methods: {
    init() {
      // given a timestamp in format yyyy-MM-dd'T'HH:mm:ss.SSS, parse into separate fields
      if (this.modelValue) {
        this.onTimestampChange(this.modelValue)
        this.updateUnixTimestamp()
      }
    },
    handleKeyPress(nextField, event, allowDecimal = false) {
      const allowedKeys = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "Backspace",
        "ArrowLeft",
        "ArrowRight",
        "Delete",
        "Tab",
        "Enter",
      ]
      if (allowDecimal) {
        allowedKeys.push(".")
      }
      if (!allowedKeys.includes(event.key)) {
        // Prevent default action for non-numeric and edit keys
        event.preventDefault()
      }
      if (nextField && event.key === "Enter") {
        // if Enter, move to the next field
        event.preventDefault()
        if (nextField && this.$refs[nextField]) {
          this.$refs[nextField].focus()
        }
      }
    },
    okHandler() {
      let date = `${this.year}-${this.month}-${this.day}T${this.hour}:${this.minutes}:${this.seconds}`
      if (this.timezone !== "UTC") {
        let dateInTimeZone = zonedTimeToUtc(date, this.timezone)
        date = format(dateInTimeZone, "yyyy-MM-dd'T'HH:mm:ss.SSS")
      }
      this.$emit("update:modelValue", date)
      this.$emit("ok")
    },
    updateUnixTimestamp() {
      // build Date object from fields
      const date = `${this.year}-${this.month}-${this.day}T${this.hour}:${this.minutes}:${this.seconds}`
      const dateObject = zonedTimeToUtc(date, this.timezone)
      const timestampInMilliseconds = dateObject.getTime()
      this.unixTimestamp = Math.floor(timestampInMilliseconds)
    },
    handlePaste(event) {
      event.preventDefault()
      const clipboardData = event.clipboardData || window.clipboardData
      let pastedData = clipboardData.getData("Text")
      // check to see if pastedData is a valid Unix timestamp
      let milliseconds = 0
      let convertedData = pastedData
      try {
        if (pastedData.length == 13) {
          milliseconds = pastedData.slice(10, 13)
          convertedData = pastedData.slice(0, 10)
        }
        if (pastedData.length == 14 && pastedData[10] === ".") {
          milliseconds = pastedData.slice(11, 14)
          convertedData = pastedData.slice(0, 10)
        }
        const dateInUtc = fromUnixTime(parseInt(convertedData))
        const dateInTimeZone = utcToZonedTime(dateInUtc, this.timezone)
        let isoFormatString = format(dateInTimeZone, "yyyy-MM-dd'T'HH:mm:ss")
        if (milliseconds) {
          isoFormatString += `.${milliseconds}`
        }
        this.unixTimestamp = pastedData
        this.onTimestampChange(isoFormatString)
      } catch {
        return
      }
    },
    onTimestampChange(dateTime) {
      if (dateTime) {
        let timeString = dateTime.split("T")
        const [year, month, day] = timeString[0].split("-")
        const [hours, minutes, seconds] = timeString[1].split(":")
        this.year = year
        this.month = month
        this.day = day
        this.hour = hours
        this.minutes = minutes
        this.seconds = removeEndingZ(seconds)
      }
    },
    highlightText(event) {
      setTimeout(() => {
        event.target.select()
      }, 0)
    },
    validateMonth() {
      if (!this.month || isNaN(this.month) || this.month < 1) {
        this.month = "01"
      } else if (this.month.length === 1) {
        this.month = `0${this.month}`
      } else if (this.month > 12) {
        this.month = "12"
      }
      this.updateUnixTimestamp()
    },
    validateDay() {
      if (!this.day || isNaN(this.day) || this.day < 1) {
        this.day = "01"
      } else if (this.day.length === 1) {
        this.day = `0${this.day}`
      } else if (this.day > 31) {
        this.day = "31"
      }
      this.updateUnixTimestamp()
    },
    validateYear() {
      if (!this.year || isNaN(this.year)) {
        this.year = "2024"
      } else if (this.year < 1000) {
        this.year = "1000"
      }
      this.updateUnixTimestamp()
    },
    validateHour() {
      if (!this.hour || isNaN(this.hour)) {
        this.hour = "00"
      } else if (this.hour.length === 1) {
        this.hour = `0${this.hour}`
      } else if (this.hour > 23) {
        this.hour = "23"
      }
      this.updateUnixTimestamp()
    },
    validateMinutes() {
      if (!this.minutes || isNaN(this.minutes)) {
        this.minutes = "00"
      } else if (this.minutes.length === 1) {
        this.minutes = `0${this.minutes}`
      } else if (this.minutes > 59) {
        this.minutes = "59"
      }
      this.updateUnixTimestamp()
    },
    validateSeconds() {
      if (!this.seconds || isNaN(this.seconds)) {
        this.seconds = "0"
      } else if (this.seconds >= 60) {
        this.seconds = "59"
      }
      this.seconds = parseFloat(this.seconds).toFixed(3)
      if (this.seconds < 10) {
        this.seconds = `0${this.seconds}`
      }
      this.updateUnixTimestamp()
    },
    filterNumericInt(field, value, isYear = false) {
      // Remove non-numeric characters
      const numericValue = value.replace(/[^0-9]/g, "")
      if (!numericValue || isNaN(numericValue)) {
        this[field] = isYear ? "2024" : "01"
      } else {
        this[field] = numericValue
      }
    },
    filterNumeric(field, value, nextField) {
      if (value.length >= 2) {
        // Move focus to the next field if max length is reached
        if (nextField && this.$refs[nextField]) {
          this.$refs[nextField].focus()
        }
      } else {
        this.filterNumericInt(field, value, false)
      }
    },
    filterNumericYear(field, value, nextField) {
      if (value.length >= 4) {
        // Move focus to the next field if max length is reached
        if (nextField && this.$refs[nextField]) {
          this.$refs[nextField].focus()
        }
      } else {
        this.filterNumericInt(field, value, true)
      }
    },
    filterNumericSeconds(field, value) {
      // Remove non-numeric characters but allow decimal point
      const numericValue = value.replace(/[^0-9.]/g, "")
      if (!numericValue || isNaN(numericValue)) {
        this[field] = "00"
      } else {
        this[field] = numericValue
      }
    },
  },
}
</script>

<style scoped>
.slash-space {
  margin-top: 10px;
  margin-left: 1px;
  margin-right: 1px;
}
.colon-space {
  margin-top: 10px;
  margin-left: 0px;
  margin-right: 1px;
}
.custom-underline {
  position: relative;
  padding-bottom: 2px;
}

.custom-underline::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background-color: rgba(0, 0, 0, 0.38);
}

.paste-only input {
  pointer-events: none; /* Make the input non-editable */
}
</style>
