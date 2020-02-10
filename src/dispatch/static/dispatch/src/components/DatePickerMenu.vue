<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    :return-value.sync="date"
    transition="scale-transition"
    offset-y
    min-width="290px"
  >
    <template v-slot:activator="{ on }">
      <v-text-field v-model="date" label="Select Date" prepend-icon="event" readonly v-on="on"></v-text-field>
    </template>
    <v-date-picker v-model="date" no-title scrollable>
      <v-spacer></v-spacer>
      <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
      <v-btn text color="primary" @click="$refs.menu.save(date)">OK</v-btn>
    </v-date-picker>
  </v-menu>
</template>

<script>
export default {
  name: "DatePickerMenu",

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
    date: {
      get() {
        if (!this.value) {
          return new Date().toISOString().substring(0, 10)
        }
        return this.value.substring(0, 10)
      },
      set(value) {
        if (!this.value) {
          value = value + "T" + new Date().toISOString().substring(11, 19)
        } else {
          value = value + "T" + this.value.substring(11, 19)
        }
        this.$emit("input", value)
      }
    }
  }
}
</script>
