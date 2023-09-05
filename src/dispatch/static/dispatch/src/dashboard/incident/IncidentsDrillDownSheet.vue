<template>
  <v-navigation-drawer app clipped right bottom width="500">
    <template #prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-subtitle>Details</v-list-item-subtitle>
        </v-list-item-content>
        <v-btn icon color="secondary" @click="hideSheet()">
          <v-icon>close</v-icon>
        </v-btn>
      </v-list-item>
    </template>
    <incident-drill-down-table :items="items" />
  </v-navigation-drawer>
</template>

<script>
import IncidentDrillDownTable from "@/dashboard/incident/IncidentDrillDownTable.vue"

export default {
  name: "IncidentsDrillDownSheet",

  props: {
    items: {
      default: function () {
        return []
      },
      type: Array,
    },
  },

  methods: {
    hideSheet() {
      this.$emit("input", false)
    },
  },

  components: {
    IncidentDrillDownTable,
  },
}
</script>
