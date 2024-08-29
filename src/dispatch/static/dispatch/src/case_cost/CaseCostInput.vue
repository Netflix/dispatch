<template>
  <v-container>
    <v-row>
      <v-list>
        <v-list-item target="_blank">
          <v-list-item-title>Add Cost</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-row>
    <v-row align="center">
      <v-col cols="12" sm="7">
        <case-cost-type-combobox v-model="case_cost_type" />
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field type="number" label="Amount" v-model.number="amount" prefix="$" />
      </v-col>
      <v-col cols="12" sm="1">
        <v-tooltip location="bottom">
          <template #activator="{ props }">
            <v-btn size="small" icon variant="text" @click="addCaseCost()" v-bind="props">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <span>Add Cost</span>
        </v-tooltip>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import CaseCostTypeCombobox from "@/case_cost_type/CaseCostTypeCombobox.vue"

export default {
  name: "CaseCostInput",

  components: {
    CaseCostTypeCombobox,
  },

  data() {
    return {
      amount: null,
      case_cost_type: null,
    }
  },

  methods: {
    addCaseCost() {
      if (this.amount !== null && this.case_cost_type !== null) {
        // Passing data to parent component
        this.$emit("add", { amount: this.amount, case_cost_type: this.case_cost_type })

        // Resetting default values
        this.amount = null
        this.case_cost_type = null
      }
    },
  },
}
</script>
