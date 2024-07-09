<template>
  <v-list>
    <v-list-item target="_blank">
      <v-list-item-title>Total Cost</v-list-item-title>

      <template #append>{{ toUSD(totalCost) }} </template>
    </v-list-item>
    <v-divider />
    <span v-for="(cost, index) in case_costs" :key="index">
      <v-list-item target="_blank">
        <template #prepend v-if="cost.case_cost_type.editable">
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn size="small" icon variant="text" @click="removeCaseCost(index)" v-bind="props">
                <v-icon>mdi-minus</v-icon>
              </v-btn>
            </template>
            <span>Remove Cost</span>
          </v-tooltip>
        </template>

        <v-list-item-title>
          {{ cost.case_cost_type.name }}
        </v-list-item-title>
        <v-list-item-subtitle>{{ cost.case_cost_type.description }}</v-list-item-subtitle>

        <template #append>
          {{ toUSD(cost.amount) }}
        </template>
      </v-list-item>
      <v-divider />
    </span>

    <v-col cols="12">
      <case-cost-input @add="addCaseCost" />
    </v-col>
  </v-list>
</template>

<script>
import { mapMutations } from "vuex"
import { mapMultiRowFields } from "vuex-map-fields"
import { toUSD } from "@/filters"

import CaseCostInput from "@/case_cost/CaseCostInput.vue"

export default {
  name: "CaseCostsTab",

  components: {
    CaseCostInput,
  },

  setup() {
    return { toUSD }
  },

  computed: {
    ...mapMultiRowFields("case_management", ["selected.case_costs", "selected"]),

    totalCost() {
      console.log('getting total cost')
      var cost = this.case_costs.reduce((accumulator, item) => {
        return accumulator + item.amount
      }, 0)
      console.log('cost is')
      console.log(cost)
      return cost
    },
  },

  methods: {
    ...mapMutations("case_management", ["addCaseCost", "removeCaseCost", "getCostInfo"]),
  },
}
</script>
