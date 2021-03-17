<template>
  <div>
    <v-menu v-model="menu" bottom right transition="scale-transition" origin="top left">
      <template v-slot:activator="{ on }">
        <v-chip pill small v-on="on">
          <v-avatar color="teal" left>
            <span class="white--text">{{ incident_cost.incident_cost_type.name | initials }}</span>
          </v-avatar>
          {{ incident_cost.amount | toUSD }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <v-list-item-avatar color="teal">
              <span class="white--text">{{ incident_cost.incident_cost_type.name | initials }}</span>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>{{ incident_cost.incident_cost_type.name }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ incident_cost.incident_cost_type.description }}
              </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
        <v-list>
          <v-list-item>
            <v-list-item-action>
              <v-icon>mdi-currency-usd</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ incident_cost.amount | toUSD }}</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "IncidentCost",

  data: () => ({
    menu: false
  }),

  props: {
    incident_cost: {
      type: Object,
      required: false
    }
  }
}
</script>
