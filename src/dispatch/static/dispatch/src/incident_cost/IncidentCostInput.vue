<template>
  <v-container>
    <v-row no-gutter>
      <span class="subtitle-2">Additional Incident Costs</span>
      <v-spacer />
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn small icon @click="addIncidentCost()" v-on="on"><v-icon>add</v-icon></v-btn>
        </template>
        <span>Add Incident Cost</span>
      </v-tooltip>
    </v-row>
    <span v-for="(incident_cost, idx) in incident_costs" :key="idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeIncidentCost(idx)" v-on="on">
                <v-icon>remove</v-icon>
              </v-btn>
            </template>
            <span>Remove Incident Cost</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="10">
          <incident-cost-type-combobox
            @input="setIncidentCostType({ incident_cost_type: $event })"
            label="Type"
            :value="incident_cost_type"
          />
          <v-text-field label="Amount" v-model="amount" prefix="$">
          </v-text-field>
        </v-col>
      </v-row>
    </span>
  </v-container>
</template>

<script>
import IncidentCostTypeCombobox from "@/incident_cost_type/IncidentCostTypeCombobox.vue"

export default {
  name: "IncidentCostInput",

  components: {
    IncidentCostTypeCombobox
  },

  data() {
    return {
      amount: 0,
      incident_cost_type: null
    }
  },

  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    }
  },

  computed: {
    incident_costs: {
      get() {
        return [...this.value]
      }
    }
  },

  methods: {
    addIncidentCost() {
      console.log(this.amount)
      console.log(this.incident_cost_type)
      console.log(this.incident_costs)
      console.log("Before adding an incident costs in IncidentCostInput.vue")
      this.incident_costs.push({ amount: this.amount, incident_cost_type: this.incident_cost_type })
      this.$emit("input", this.incident_costs)
      console.log("After adding an incident costs in IncidentCostInput.vue")
      this.amount = 0 // value is not getting resetted
      this.incident_cost_type = null // value is not getting resetted
      console.log(this.amount)
      console.log(this.incident_cost_type)
    },
    removeIncidentCost(idx) {
      console.log("Before removing an incident costs in IncidentCostInput.vue")
      this.incident_costs.splice(idx)
      this.$emit("input", this.incident_costs)
      console.log("After removing an incident costs in IncidentCostInput.vue")
    },
    setIncidentCostType(event) {
      console.log("Before setting the incident cost type in IncidentCostInput.vue")
      console.log(this.incident_cost_type)
      console.log(event.incident_cost_type)
      this.incident_cost_type = event.incident_cost_type
      // this.$emit("input", this.incident_costs) Do I need to emit here?
      console.log("After setting the incident cost type in IncidentCostInput.vue")
      console.log(this.incident_cost_type)
    }
  }
}
</script>
