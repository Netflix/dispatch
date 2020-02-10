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
      ></v-text-field>
    </template>
    <v-time-picker v-model="time" full-width @click:minute="$refs.menu.save(time)"></v-time-picker>
  </v-menu>
</template>

<script>
export default {
  name: "TimePickerMenu",

  props: {
    value: {
      type: String
    }
  },

  data() {
    return {
      menu: false
    }
  },

  computed: {
    time: {
      get() {
        if (!this.value) {
          return new Date().toISOString().substring(11, 16)
        }
        return this.value.substring(11, 16)
      },
      set(value) {
        if (!this.value) {
          value = new Date().toISOString().substring(0, 10) + "T" + value
        } else {
          value = this.value.substring(0, 10) + "T" + value
        }
        this.$emit("input", value)
      }
    }
  }
}
</script>
