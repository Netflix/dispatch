<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    :nudge-right="40"
    :return-value.sync="value"
    transition="scale-transition"
    offset-y
    max-width="290px"
    min-width="290px"
  >
    <template v-slot:activator="{ on }">
      <v-text-field
        v-model="value"
        label="Select Time"
        prepend-icon="access_time"
        readonly
        v-on="on"
      />
    </template>
    <v-time-picker v-model="value" color="info" full-width>
      <v-spacer />
      <v-btn text color="info" @click="menu = false"> Cancel </v-btn>
      <v-btn text color="info" @click="$refs.menu.save(value)"> OK </v-btn>
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
}
</script>
