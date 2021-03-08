<template>
  <!-- <v&#45;container grid&#45;list&#45;md> -->
  <!--   <v&#45;layout wrap></v&#45;layout> -->
  <!-- </v&#45;container> -->
  <div>
    <span v-for="incident_cost in incident_costs" :key="incident_cost.id">
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            {{ incident_cost.amount | toUSD }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ incident_cost.incident_cost_type.name }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider />
    </span>
  </div>
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
    // ...mapFields("incident", ["selected.id", "selected.incident_costs"])
    ...mapFields("incident", ["selected.incident_costs"])
  }
}
</script>
