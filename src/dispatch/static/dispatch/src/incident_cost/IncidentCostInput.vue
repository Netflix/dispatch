<template>
  <v-container>
    <v-row>
      <span class="subtitle-2">Add Cost</span>
      <v-spacer />
    </v-row>
    <v-row align="center">
      <v-col cols="12" sm="7">
        <incident-cost-type-select v-model="incident_cost_type" />
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field type="number" label="Amount" v-model.number="amount" prefix="$">
        </v-text-field>
      </v-col>
      <v-col cols="12" sm="1">
        <v-tooltip bottom>
          <template v-slot:activator="{ on }">
            <v-btn small icon @click="addIncidentCost()" v-on="on"><v-icon>add</v-icon></v-btn>
          </template>
          <span>Add Cost</span>
        </v-tooltip>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import IncidentCostTypeSelect from "@/incident_cost_type/IncidentCostTypeSelect.vue"

export default {
  name: "IncidentCostInput",

  components: {
    IncidentCostTypeSelect
  },

  data() {
    return {
      amount: null,
      incident_cost_type: null
    }
  },

  methods: {
    addIncidentCost() {
      if (this.amount !== null && this.incident_cost_type !== null) {
        // Passing data to parent component
        this.$emit("input", { amount: this.amount, incident_cost_type: this.incident_cost_type })

        // Resetting default values
        this.amount = null
        this.incident_cost_type = null
      }
    }
  }
}
</script>
