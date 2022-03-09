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
        :label="label"
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

import endOfMonth from "date-fns/endOfMonth"
import endOfYear from "date-fns/endOfYear"
import parseISO from "date-fns/fp/parseISO"
import startOfMonth from "date-fns/startOfMonth"
import startOfYear from "date-fns/startOfYear"
import subDays from "date-fns/subDays"
import subMonths from "date-fns/subMonths"
import subYears from "date-fns/subYears"
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
    label: {
      type: String,
      default: "Reported At",
    },
  },

  data() {
    return {
      menu: false,
      windowRanges: [
        { title: "Today", window: { start: today(), end: today() } },
        { title: "This Month", window: { start: startOfMonth(today()), end: today() } },
        {
          title: "This Quarter",
          window: { start: startOfQuarter(today()), end: endOfQuarter(today()) },
        },
        {
          title: "This Year",
          window: { start: startOfYear(today()), end: endOfYear(today()) },
        },
        { title: "Yesterday", window: { start: subDays(today(), 1), end: subDays(today(), 1) } },
        { title: "Last 7 Days", window: { start: subDays(today(), 7), end: today() } },
        { title: "Last 30 Days", window: { start: subDays(today(), 30), end: today() } },
        {
          title: "Last Month",
          window: {
            start: startOfMonth(subMonths(today(), 1)),
            end: endOfMonth(subMonths(today(), 1)),
          },
        },
        {
          title: "Last Quarter",
          window: {
            start: startOfQuarter(subQuarters(today(), 1)),
            end: endOfQuarter(subQuarters(today(), 1)),
          },
        },
        {
          title: "Last Year",
          window: {
            start: startOfYear(subYears(today(), 1)),
            end: endOfYear(subYears(today(), 1)),
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
        return {
          start: null,
          end: null,
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
        start: this.toLocalISOString(range.start),
        end: this.toLocalISOString(range.end),
      }
    },
    clearWindowRange: function () {
      this.window = {}
    },
    setWindowStart: function (start) {
      start = parseISO(start)
      start.setHours(0, 0, 0, 0)
      this.window = {
        start: this.toLocalISOString(start),
        end: this.window.end,
      }
    },
    setWindowEnd: function (end) {
      end = parseISO(end)
      end.setHours(23, 59, 59, 999)
      this.window = {
        start: this.window.start,
        end: this.toLocalISOString(end),
      }
    },
    toLocalISOString: function (date) {
      let tzOffset = date.getTimezoneOffset() * 60000 // offset in milliseconds
      return new Date(date - tzOffset).toISOString().slice(0, -1)
    },
  },
}
</script>
