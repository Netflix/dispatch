<template>
  <v-list>
    <v-list-item target="_blank">
      <v-list-item-title>Total Cost</v-list-item-title>

      <template #append>{{ toUSD(totalCost) }} </template>
    </v-list-item>
    <v-divider />
    <span v-for="(cost, index) in incident_costs" :key="index">
      <v-list-item target="_blank">
        <template #prepend v-if="cost.incident_cost_type.editable">
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn
                size="small"
                icon
                variant="text"
                @click="removeIncidentCost(index)"
                v-bind="props"
              >
                <v-icon>mdi-minus</v-icon>
              </v-btn>
            </template>
            <span>Remove Cost</span>
          </v-tooltip>
        </template>

        <v-list-item-title>
          {{ cost.incident_cost_type.name }}
        </v-list-item-title>
        <v-list-item-subtitle>{{ cost.incident_cost_type.description }}</v-list-item-subtitle>

        <template #append>
          {{ toUSD(cost.amount) }}
        </template>
      </v-list-item>
      <v-divider />
    </span>
    <v-col cols="12">
      <incident-cost-input @add="addIncidentCost" />
    </v-col>
  </v-list>
</template>

<script>
import { mapMutations } from "vuex"
import { mapMultiRowFields } from "vuex-map-fields"
import { toUSD } from "@/filters"

import IncidentCostInput from "@/incident_cost/IncidentCostInput.vue"

export default {
  name: "IncidentCostsTab",

  components: {
    IncidentCostInput,
  },

  setup() {
    return { toUSD }
  },

  computed: {
    ...mapMultiRowFields("incident", ["selected.incident_costs"]),

    totalCost() {
      return this.incident_costs.reduce((accumulator, item) => {
        return accumulator + item.amount
      }, 0)
    },
  },

  methods: {
    ...mapMutations("incident", ["addIncidentCost", "removeIncidentCost"]),
  },
}
</script>
