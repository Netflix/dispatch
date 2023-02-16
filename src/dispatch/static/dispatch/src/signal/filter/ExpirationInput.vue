<template>
  <v-menu v-model="menu" :close-on-content-click="false" transition="scale-transition">
    <template v-slot:activator="{ on, attrs }">
      <v-text-field
        v-model="expiration"
        :label="label"
        v-bind="attrs"
        v-on="on"
        clearable
        readonly
        @click:clear="clearExpiration()"
      ></v-text-field>
    </template>
    <v-card>
      <v-row>
        <v-col>
          <v-list>
            <v-list-item-group color="primary">
              <v-list-item
                v-for="(item, index) in expirationShortcuts"
                :key="index"
                @click="setExpiration(item.expiration)"
              >
                <v-list-item-title class="text-center">{{ item.title }}</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-col>
        <v-col>
          <date-time-picker label="Expiration" v-model="expiration" />
        </v-col>
      </v-row>
      <v-card-actions>
        <v-spacer></v-spacer>
        <slot name="actions" :parent="this">
          <v-btn color="grey lighten-1" text @click.native="clearExpiration()">Clear</v-btn>
          <v-btn text @click="closeMenu()">Ok</v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script>
import { cloneDeep } from "lodash"

import addMinutes from "date-fns/addMinutes"
import addHours from "date-fns/addHours"
import addDays from "date-fns/addDays"

import DateTimePicker from "@/components/DateTimePicker.vue"

let now = function () {
  return new Date()
}

export default {
  name: "ExpirationInput",
  components: { DateTimePicker },
  props: {
    value: {
      type: [Date, String],
      default: null,
    },
    label: {
      type: String,
      default: "Expiration",
    },
  },

  data() {
    return {
      menu: false,
      expirationShortcuts: [
        { title: "5 min", expiration: addMinutes(now(), 5) },
        { title: "10 min", expiration: addMinutes(now(), 10) },
        {
          title: "30 min",
          expiration: addMinutes(now(), 30),
        },
        {
          title: "1 hr",
          expiration: addMinutes(now(), 60),
        },
        { title: "6 hrs", expiration: addHours(now(), 6) },
        { title: "12 hrs", expiration: addHours(now(), 12) },
        { title: "1 day", expiration: addDays(now(), 1) },
        {
          title: "7 days",
          expiration: addDays(now(), 7),
        },
        {
          title: "30 days",
          expiration: addDays(now(), 30),
        },
        {
          title: "60 days",
          expiration: addDays(now(), 60),
        },
      ],
    }
  },

  computed: {
    expiration: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  methods: {
    setExpiration: function (value) {
      this.expiration = this.toLocalISOString(value)
    },
    clearExpiration: function () {
      this.expiration = null
    },
    closeMenu: function () {
      this.menu = false
    },
    toLocalISOString: function (date) {
      let tzOffset = date.getTimezoneOffset() * 60000 // offset in milliseconds
      return new Date(date - tzOffset).toISOString().slice(0, -1)
    },
  },
}
</script>
