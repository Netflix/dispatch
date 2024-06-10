<template>
  <v-menu
    ref="menu"
    v-model="display"
    :close-on-content-click="false"
    max-width="280px"
    min-width="280px"
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
    <precise-date-time-picker v-model="selectedDatetime" :timezone="timezone" @ok="okHandler" />
  </v-menu>
</template>
<script>
import { parseISO } from "date-fns"
import { formatInTimeZone, format } from "date-fns-tz"
import moment from "moment-timezone"
import PreciseDateTimePicker from "@/components/PreciseDateTimePicker.vue"

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

  components: {
    PreciseDateTimePicker,
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
        ? format(parseISO(this.selectedDatetime), "yyyy-MM-dd HH:mm:ss.SSS")
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

      this.selectedDatetime = formatInTimeZone(
        initDateTime,
        this.timezone,
        "yyyy-MM-dd'T'HH:mm:ss.SSS"
      )
    },
    okHandler() {
      this.resetPicker()
      let newValue = moment.tz(this.selectedDatetime, this.timezone).toISOString()
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
        "yyyy-MM-dd'T'HH:mm:ss.SSS"
      )
    },
  },
}
</script>
