<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    transition="scale-transition"
    min-width="auto"
    offset-y
  >
    <template v-slot:activator="{ on, attrs }">
      <v-text-field
        v-model="windowRange"
        label="Reported At"
        v-bind="attrs"
        v-on="on"
        clearable
        readonly
        @click:clear="clearWindowRange()"
      ></v-text-field>
    </template>
    <v-card>
      <v-container>
        <v-row>
          <v-col>
            <v-list>
              <v-list-item-group color="primary">
                <v-list-item
                  v-for="(item, index) in windowRanges"
                  :key="index"
                  @click="setWindowRange(item.window)"
                >
                  <v-list-item-title>{{ item.title }}</v-list-item-title>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-col>
          <v-col>
            <v-text-field :value="windowStartFormatted" prepend-icon="mdi-calendar"></v-text-field>
            <v-date-picker
              color="primary"
              no-title
              :value="window.start"
              @input="setWindowStart($event)"
            ></v-date-picker>
          </v-col>
          <v-col>
            <v-text-field v-model="windowEndFormatted" prepend-icon="mdi-calendar"></v-text-field>
            <v-date-picker
              color="primary"
              no-title
              :value="window.end"
              @input="setWindowEnd($event)"
            ></v-date-picker>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-menu>
</template>

<script>
import { cloneDeep } from "lodash"

import subMonths from "date-fns/subMonths"
import subDays from "date-fns/subDays"
import lastDayOfYear from "date-fns/lastDayOfYear"
import subYears from "date-fns/subYears"
import startOfYear from "date-fns/startOfYear"
import startOfMonth from "date-fns/startOfMonth"
import lastDayOfMonth from "date-fns/lastDayOfMonth"
import { endOfQuarter, startOfQuarter, subQuarters } from "date-fns"

let today = function () {
  let now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

export default {
  name: "IncidentWindowInput",
  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  data() {
    return {
      menu: false,
      windowRanges: [
        { title: "Today", window: { start: today(), end: today() } },
        { title: "Yesterday", window: { start: subDays(today(), 1), end: subDays(today(), 1) } },
        { title: "Last 7 Days", window: { start: subDays(today(), 7), end: today() } },
        { title: "Last 30 Days", window: { start: subDays(today(), 30), end: today() } },
        { title: "This Month", window: { start: startOfMonth(today()), end: today() } },
        {
          title: "Last Month",
          window: { start: subMonths(today(), 1), end: lastDayOfMonth(subMonths(today(), 1)) },
        },
        {
          title: "This Quarter",
          window: { start: startOfQuarter(today()), end: endOfQuarter(today()) },
        },
        {
          title: "Last Quarter",
          window: {
            start: startOfQuarter(subQuarters(today(), 1)),
            end: endOfQuarter(subQuarters(today(), 1)),
          },
        },
        {
          title: "This Year",
          window: { start: startOfYear(today()), end: lastDayOfYear(today()) },
        },
        {
          title: "Last Year",
          window: {
            start: startOfYear(subYears(today(), 1)),
            end: lastDayOfYear(subYears(today(), 1)),
          },
        },
      ],
    }
  },

  computed: {
    windowRange: function () {
      return `${this.windowStartFormatted} ~ ${this.windowEndFormatted}`
    },
    window: {
      get() {
        if (Object.keys(this.value).length > 1) {
          return cloneDeep(this.value)
        }
        let start = subMonths(today(), 6).setHours(0, 0, 0, 0)
        let end = today().setHours(23, 59, 59, 999)
        return {
          start: start.toISOString(),
          end: end.toISOString(),
        }
      },
      set(value) {
        this.$emit("input", value)
      },
    },
    windowStartFormatted() {
      if (this.window.start) {
        return this.window.start.substr(0, 10)
      }
      return ""
    },
    windowEndFormatted() {
      if (this.window.end) {
        return this.window.end.substr(0, 10)
      }
      return ""
    },
  },

  methods: {
    setWindowRange: function (range) {
      range.start.setHours(0, 0, 0, 0)
      range.end.setHours(23, 59, 59, 999)
      this.window = {
        start: range.start.toISOString(),
        end: range.end.toISOString(),
      }
    },
    clearWindowRange: function () {
      this.window = {}
    },
    setWindowStart: function (start) {
      start.setHours(0, 0, 0, 0)
      this.window = {
        start: start.toISOString(),
        end: this.window.end.toISOString(),
      }
    },
    setWindowEnd: function (end) {
      end.setHours(23, 59, 59, 999)
      this.window = {
        start: this.window.start.toISOString(),
        end: end.toISOString(),
      }
    },
  },
}
</script>
