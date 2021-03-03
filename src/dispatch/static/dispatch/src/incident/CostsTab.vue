<template>
  <v-container grid-list-md>
    <v-layout wrap></v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
// import { ValidationProvider, extend } from "vee-validate"
import { extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"
// import ParticipantSelect from "@/incident/ParticipantSelect.vue"

extend("required", {
  ...required,
  message: "This field is required"
})

export default {
  name: "IncidentCostsTab",

  // components: {
  //   ValidationProvider
  // },

  computed: {
    ...mapFields("incident", ["selected.id", "selected.incident_costs"])
  }
}
</script>
