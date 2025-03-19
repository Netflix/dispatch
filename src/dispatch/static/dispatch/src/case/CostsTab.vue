<template>
  <v-list>
    <v-list-item>
      <v-row align="center" no-gutters>
        <v-col cols="12" sm="6">
          <v-tooltip max-width="500px" open-delay="50" location="bottom">
            <template #activator="{ props }">
              <div v-bind="props">
                <v-btn-toggle v-model="model" density="comfortable" color="primary">
                  <v-btn value="Classic" variant="tonal"> Classic Cost Model </v-btn>
                  <v-btn value="New" variant="tonal"> New Cost Model </v-btn>
                </v-btn-toggle>
              </div>
            </template>
            <div>
              <div class="text-subtitle-1 mb-2">Cost Model Information</div>
              <div class="mb-1">
                <strong>Classic Cost Model:</strong>
                Traditional cost calculation method based on participant role time.
              </div>
              <div>
                <strong>New Cost Model:</strong>
                Cost calculation method based on participant activity time.
              </div>
            </div>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="6" class="d-flex flex-column align-end">
          <div class="font-weight-bold text-primary">
            {{ model === "New" ? toUSD(totalCostNew) : toUSD(totalCostClassic) }}
          </div>
          <div class="text-caption text-medium-emphasis">Total Cost</div>
        </v-col>
      </v-row>
    </v-list-item>
    <v-divider />
    <span v-for="(cost, index) in case_costs" :key="index">
      <v-list-item
        target="_blank"
        v-if="cost.case_cost_type.model_type == model || !cost.case_cost_type.model_type"
      >
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
