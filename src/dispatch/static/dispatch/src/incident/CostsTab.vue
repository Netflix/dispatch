<template>
  <v-container grid-list-md>
    <v-layout wrap>
      <v-flex xs12>
        <span class="subtitle-2">Total Cost: {{ totalCost | toUSD }}</span>
      </v-flex>
      <v-flex xs12>
        <span class="subtitle-2">Response Cost: {{ responseCost | toUSD }}</span>
      </v-flex>
      <v-flex xs12>
        <incident-cost-input
          @input="updateIncidentCosts({ data: $event })"
          v-model="incident_costs"
        />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import IncidentCostInput from "@/incident_cost/IncidentCostInput.vue"

export default {
  name: "IncidentCostsTab",

  components: {
    IncidentCostInput
  },

  computed: {
    ...mapFields("incident", ["selected.incident_costs"]),

    responseCost: function() {
      for (let i = 0; i < this.incident_costs.length; i++) {
        if (this.incident_costs[i].incident_cost_type.name == "Response Cost")
          return this.incident_costs[i].amount
      }
      return 0
    },

    totalCost: function() {
      var totalCost = this.incident_costs.reduce(function(accumulator, item) {
        return accumulator + item.amount
      }, 0)
      return totalCost
    }
  },

  methods: {
    updateIncidentCosts(event) {
      console.log("Before updating incident costs in CostsTab.vue")
      console.log(this.incident_costs)
      this.incident_costs = event.data
      console.log("After updating incident costs in CostsTab.vue")
      console.log(this.incident_costs)
    }
  }
}
</script>
