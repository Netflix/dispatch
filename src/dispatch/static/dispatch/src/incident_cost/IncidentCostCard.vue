<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props">
          <v-avatar color="teal" start>
            <span class="text-white">TC</span>
          </v-avatar>
          {{ toUSD(totalCost) }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <template #prepend>
              <v-avatar color="teal">
                <span class="text-white">TC</span>
              </v-avatar>
            </template>

            <v-list-item-title>Total Cost</v-list-item-title>
            <v-list-item-subtitle>
              {{ toUSD(totalCost) }}
            </v-list-item-subtitle>

            <template #append>
              <v-btn icon variant="text" @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </template>
          </v-list-item>
        </v-list>
        <span v-for="(cost, index) in incidentCosts" :key="index">
          <v-list>
            <v-list-item>
              <template #prepend>
                <v-icon>mdi-currency-usd</v-icon>
              </template>

              <v-list-item-subtitle>
                {{ cost.incident_cost_type.name }}: {{ toUSD(cost.amount) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </span>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import { toUSD } from "@/filters"

export default {
  name: "IncidentCostCard",

  data: () => ({
    menu: false,
  }),

  setup() {
    return { toUSD }
  },

  props: {
    incidentCosts: {
      type: Array,
      default: null,
    },
  },

  computed: {
    totalCost: function () {
      var totalCost = this.incidentCosts.reduce(function (accumulator, item) {
        return accumulator + item.amount
      }, 0)
      return totalCost
    },
  },
}
</script>
