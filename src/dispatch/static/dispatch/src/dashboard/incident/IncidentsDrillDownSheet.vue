<template>
  <v-navigation-drawer clipped location="right" width="500">
    <template #prepend>
      <v-list-item lines="two">
        <v-list-item-subtitle>Details</v-list-item-subtitle>

        <v-btn icon variant="text" color="secondary" @click="hideSheet()">
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
