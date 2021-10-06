<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    :nudge-right="40"
    :return-value.sync="time"
    transition="scale-transition"
    offset-y
    max-width="290px"
    min-width="290px"
  >
    <template v-slot:activator="{ on }">
      <v-text-field
        v-model="time"
        label="Select Time"
        prepend-icon="access_time"
        readonly
        v-on="on"
      />
    </template>
    <v-time-picker v-model="time" color="info" format="24hr" full-width>
      <v-spacer />
      <v-btn text color="info" @click="menu = false"> Cancel </v-btn>
      <v-btn text color="info" @click="$refs.menu.save(time)"> OK </v-btn>
    </v-time-picker>
  </v-menu>
</template>

<script>
export default {
  name: "TimePickerMenu",

  props: {
    value: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      menu: false,
    }
  },

  computed: {
    time: {
      get() {
        console.log("get")
        console.log(this.value)
        if (!this.value) {
          console.log("no value")
          var date = Date().substring(16, 21)
          console.log(date)
          return date
        }
        console.log("value")
        date = new Date(this.value + "Z").toString().substring(16, 21)
        console.log(date)
        return date
      },
      set(value) {
        console.log("set")
        console.log(this.value)
        console.log(value)
        if (!this.value) {
          console.log("no value")
          value = new Date().toISOString().substring(0, 23)
          // value = new Date().toISOString().substring(0, 10) + "T" + value
        } else {
          console.log("value")
          var date = new Date(this.value)
          console.log(date)
          console.log(date.toISOString())
          value = new Date(this.value).toISOString().substring(0, 23)
          // value = new Date(this.value).toISOString().substring(0, 10) + "T" + value
        }
        console.log(value)
        this.$emit("input", value)
      },
    },
  },
}
</script>
