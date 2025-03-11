<template>
  <v-list>
    <v-list-item target="_blank">
      <v-list-item-title>
        <v-tooltip max-width="500px" open-delay="50" location="bottom">
          <template #activator="{ props }">
            <v-switch
              v-model="model"
              :label="`Total Cost (${model})`"
              false-value="Classic"
              true-value="New"
              v-bind="props"
            />
          </template>
          <span> Toggle between Classic and New Cost model costs. </span>
        </v-tooltip>
      </v-list-item-title>
      <template #append>
        <span v-if="model == 'New'">{{ toUSD(totalCostNew) }}</span>
        <span v-else>{{ toUSD(totalCostClassic) }}</span>
      </template>
    </v-list-item>
    <v-divider />
    <span v-for="(cost, index) in case_costs" :key="index">
      <v-list-item target="_blank" v-if="cost.case_cost_type.model_type == model">
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
        <v-list-item-subtitle>
          Updated At: {{ formatRelativeDate(cost.updated_at) }}
        </v-list-item-subtitle>

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
import { formatRelativeDate } from "@/filters"

import CaseCostInput from "@/case_cost/CaseCostInput.vue"

export default {
  name: "CaseCostsTab",

  components: {
    CaseCostInput,
  },

  data: () => ({
    model: "New",
  }),

  setup() {
    return { toUSD, formatRelativeDate }
  },

  computed: {
    ...mapMultiRowFields("case_management", ["selected.case_costs", "selected"]),

    totalCostClassic() {
      var cost = this.case_costs.reduce((accumulator, item) => {
        if (item.case_cost_type.model_type == "New") {
          return accumulator
        }
        return accumulator + item.amount
      }, 0)
      return cost
    },
    totalCostNew() {
      var cost = this.case_costs.reduce((accumulator, item) => {
        if (item.case_cost_type.model_type == "Classic") {
          return accumulator
        }
        return accumulator + item.amount
      }, 0)
      return cost
    },
  },

  methods: {
    ...mapMutations("case_management", ["addCaseCost", "removeCaseCost"]),
  },
}
</script>
