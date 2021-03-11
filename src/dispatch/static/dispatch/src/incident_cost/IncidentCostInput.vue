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
    <span
      v-for="(incident_cost, idx) in incident_costs"
      :key="incident_cost.incident_cost_type.name"
    >
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
            @input="setIncidentCostType({ incident_cost_type: $event, idx: idx })"
            label="Incident Cost Type"
            :value="incident_cost_type"
          />
        </v-col>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="addCost(incident_cost)" v-on="on">
                <v-icon>add</v-icon>
              </v-btn>
            </template>
            <span>Add Cost</span>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row align="center" dense v-for="meta in plugin.metadata" :key="meta.key">
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeItem(plugin)" v-on="on"
                ><v-icon>remove</v-icon></v-btn
              >
            </template>
            <span>Remove Item</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field label="Cost Type" v-model="incident_cost.type" type="text"></v-text-field>
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field
            label="Cost Amount"
            v-model="incident_cost.amount"
            type="text"
          ></v-text-field>
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

  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    }
  },

  computed: {
    incident_cost_types: {
      get() {
        return [...this.value]
      }
    }
  },

  methods: {
    addIncidentCost() {
      this.incident_costs.push({ amount: null })
      // this.incident_costs.push({ amount: null, metadata: [{ key: "", value: "" }] })
      this.$emit("input", this.incident_costs)
    },
    removeIncidentCost(idx) {
      this.incident_costs.splice(idx)
      this.$emit("input", this.incident_costs)
    },
    addCost(incident_cost) {
      incident_cost.push({ key: null, value: null })
      this.$emit("input", this.incident_costs)
    }
    // removeItem(plugin, idx) {
    //   plugin.metadata.splice(idx)
    //   this.$emit("input", this.plugins)
    // }
    // setPlugin(event) {
    //   if (!event.plugin.metadata) {
    //     event.plugin.metadata = [{ key: null, value: null }]
    //   }
    //   this.plugins[event.idx] = event.plugin
    //   this.$emit("input", this.plugins)
    // }
  }
}
</script>
