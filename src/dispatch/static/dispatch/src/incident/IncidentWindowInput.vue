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
            <v-text-field v-model="window.start" prepend-icon="mdi-calendar"></v-text-field>
            <v-date-picker
              color="primary"
              no-title
              v-bind:value="window.start"
              v-on:input="setWindowStart($event)"
            ></v-date-picker>
          </v-col>
          <v-col>
            <v-text-field v-model="window.end" prepend-icon="mdi-calendar"></v-text-field>
            <v-date-picker
              color="primary"
              no-title
              v-bind:value="window.end"
              v-on:input="setWindowEnd($event)"
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
      return `${this.window.start || ""} ~ ${this.window.end || ""}`
    },
    window: {
      get() {
        if (Object.keys(this.value).length > 1) {
          return cloneDeep(this.value)
        }
        return {
          start: subMonths(today(), 6).toISOString().substr(0, 10),
          end: today().toISOString().substr(0, 10),
        }
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  methods: {
    setWindowRange: function (range) {
      this.window = {
        start: range.start.toISOString().substr(0, 10),
        end: range.end.toISOString().substr(0, 10),
      }
    },
    clearWindowRange: function () {
      this.window = {}
    },
    setWindowStart: function (start) {
      this.window = {
        start: start,
        end: this.window.end,
      }
    },
    setWindowEnd: function (end) {
      this.window = {
        start: this.window.start,
        end: end,
      }
    },
  },
}
</script>
