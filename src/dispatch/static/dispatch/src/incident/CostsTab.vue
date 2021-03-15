<template>
  <v-list>
    <v-list-item target="_blank">
      <v-list-item-content>
        <v-list-item-title>Total Cost</v-list-item-title>
      </v-list-item-content>
      <v-list-item-action>{{ totalCost | toUSD }} </v-list-item-action>
    </v-list-item>
    <v-divider />
    <span v-for="(cost, index) in incident_costs" :key="`cost-${index}`">
      <v-list-item target="_blank">
        <v-list-item-icon>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeIncidentCost(index)" v-on="on">
                <v-icon>remove</v-icon>
              </v-btn>
            </template>
            <span>Remove Cost</span>
          </v-tooltip>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            {{ cost.incident_cost_type.name }}
          </v-list-item-title>
          <v-list-item-subtitle>{{ cost.incident_cost_type.description }}</v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-action>{{ cost.amount | toUSD }}</v-list-item-action>
      </v-list-item>
      <v-divider />
    </span>
    <v-flex xs12>
      <incident-cost-input @input="addIncidentCost($event)" />
    </v-flex>
  </v-list>
</template>

<script>
import { mapMutations } from "vuex"
import { mapMultiRowFields } from "vuex-map-fields"
import IncidentCostInput from "@/incident_cost/IncidentCostInput.vue"

export default {
  name: "IncidentCostsTab",

  components: {
    IncidentCostInput
  },

  computed: {
    ...mapMultiRowFields("incident", ["selected.incident_costs"]),

    totalCost: function() {
      var totalCost = this.incident_costs.reduce(function(accumulator, item) {
        return accumulator + item.amount
      }, 0)
      return totalCost
    }
  },

  methods: {
    ...mapMutations("incident", ["addIncidentCost", "removeIncidentCost"])
  }
}
</script>
