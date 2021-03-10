<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            Response Cost
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ 550 | toUSD }}
          </v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-content>
          <v-list-item-title>
            Additional Costs
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ 550 | toUSD }}
          </v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-content>
          <v-list-item-title>
            Total Cost
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ 500 | toUSD }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider />
    </v-layout>
  </v-container>
  <!-- <div> -->
  <!--   <span v&#45;for="incident_cost in incident_costs" :key="incident_cost.id"> -->
  <!--     <v&#45;list&#45;item> -->
  <!--       <v&#45;list&#45;item&#45;content> -->
  <!--         <v&#45;list&#45;item&#45;title> -->
  <!--           {{ incident_cost.amount | toUSD }} -->
  <!--         </v&#45;list&#45;item&#45;title> -->
  <!--         <v&#45;list&#45;item&#45;subtitle> -->
  <!--           {{ incident_cost.incident_cost_type.name }} -->
  <!--         </v&#45;list&#45;item&#45;subtitle> -->
  <!--       </v&#45;list&#45;item&#45;content> -->
  <!--     </v&#45;list&#45;item> -->
  <!-- <v&#45;divider /> -->
  <!--   </span> -->
  <!-- </div> -->
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
