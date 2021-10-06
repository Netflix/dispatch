<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    :return-value.sync="value"
    transition="scale-transition"
    offset-y
    min-width="290px"
  >
    <template v-slot:activator="{ on }">
      <v-text-field v-model="value" label="Select Date" prepend-icon="event" readonly v-on="on" />
    </template>
    <v-date-picker color="info" v-model="value" no-title scrollable>
      <v-spacer />
      <v-btn text color="info" @click="menu = false"> Cancel </v-btn>
      <v-btn text color="info" @click="$refs.menu.save(value)"> OK </v-btn>
    </v-date-picker>
  </v-menu>
</template>

<script>
export default {
  name: "DatePickerMenu",

  props: {
    value: {
      type: String,
      default: "",
    },
  },

  data() {
    return {
      menu: false,
    }
  },
}
</script>
