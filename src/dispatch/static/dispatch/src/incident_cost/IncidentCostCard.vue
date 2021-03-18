<template>
  <div>
    <v-menu v-model="menu" bottom right transition="scale-transition" origin="top left">
      <template v-slot:activator="{ on }">
        <v-chip pill small v-on="on">
          <v-avatar color="teal" left>
            <span class="white--text">{{ "Total Cost" | initials }}</span>
          </v-avatar>
          {{ totalCost | toUSD }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <v-list-item-avatar color="teal">
              <span class="white--text">{{ "Total Cost" | initials }}</span>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>{{ "Total Cost" }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ totalCost | toUSD }}
              </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
        <span v-for="(cost, index) in incident_costs" :key="index">
          <v-list>
            <v-list-item>
              <v-list-item-action>
                <v-icon>mdi-currency-usd</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>
                {{ cost.incident_cost_type.name }}: {{ cost.amount | toUSD }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </span>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "IncidentCostCard",

  data: () => ({
    menu: false
  }),

  props: {
    incident_costs: {
      type: Array
    }
  },

  computed: {
    totalCost: function() {
      var total_cost = this.incident_costs.reduce(function(accumulator, item) {
        return accumulator + item.amount
      }, 0)
      return total_cost
    }
  }
}
</script>
