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
      <!-- TODO: use vuetify picker components -->
      <v-card-text>
        <v-text-field v-model="selectedDatetime" type="datetime-local" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-lighten-1" variant="text" @click="clearHandler">Clear</v-btn>
        <v-btn variant="text" @click="okHandler">Ok</v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>
<script>
import { parseISO } from "date-fns"
import { formatInTimeZone, format } from "date-fns-tz"
import moment from "moment-timezone"

export default {
  name: "DateTimePickerMenu",

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
    timezone: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      display: false,
      selectedDatetime: null,
    }
  },

  mounted() {
    this.init()
  },

  computed: {
    formattedDatetime() {
      return this.selectedDatetime
        ? format(parseISO(this.selectedDatetime), "yyyy-MM-dd HH:mm")
        : ""
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
      } else if (typeof this.modelValue === "string") {
        initDateTime = parseISO(this.modelValue)
      }

      this.selectedDatetime = formatInTimeZone(initDateTime, this.timezone, "yyyy-MM-dd'T'HH:mm")
    },
    okHandler() {
      this.resetPicker()
      let newValue = moment.tz(this.selectedDatetime, this.timezone).utc().format()
      this.$emit("update:modelValue", newValue)
    },
    clearHandler() {
      this.resetPicker()
      this.$emit("update:modelValue", null)
    },
    resetPicker() {
      this.display = false
    },
    showTimePicker() {
      this.activeTab = 1
    },
  },
  watch: {
    modelValue() {
      this.init()
    },
    timezone() {
      this.selectedDatetime = formatInTimeZone(
        parseISO(this.modelValue),
        this.timezone,
        "yyyy-MM-dd'T'HH:mm"
      )
    },
  },
}
</script>
