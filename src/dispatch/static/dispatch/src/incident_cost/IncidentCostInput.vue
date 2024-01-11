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
        <incident-cost-type-combobox v-model="incident_cost_type" />
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field type="number" label="Amount" v-model.number="amount" prefix="$" />
      </v-col>
      <v-col cols="12" sm="1">
        <v-tooltip location="bottom">
          <template #activator="{ props }">
            <v-btn size="small" icon variant="text" @click="addIncidentCost()" v-bind="props">
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
import IncidentCostTypeCombobox from "@/incident_cost_type/IncidentCostTypeCombobox.vue"

export default {
  name: "IncidentCostInput",

  components: {
    IncidentCostTypeCombobox,
  },

  data() {
    return {
      amount: null,
      incident_cost_type: null,
    }
  },

  methods: {
    addIncidentCost() {
      if (this.amount !== null && this.incident_cost_type !== null) {
        // Passing data to parent component
        this.$emit("add", { amount: this.amount, incident_cost_type: this.incident_cost_type })

        // Resetting default values
        this.amount = null
        this.incident_cost_type = null
      }
    },
  },
}
</script>
