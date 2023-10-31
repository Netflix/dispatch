<template>
  <v-navigation-drawer location="right" width="500">
    <template #prepend>
      <v-list-item lines="two">
        <v-list-item-subtitle>Details</v-list-item-subtitle>

        <template #append>
          <v-btn icon variant="text" color="secondary" @click="hideSheet()">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
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
      this.$emit("update:modelValue", false)
    },
  },

  components: {
    IncidentDrillDownTable,
  },
}
</script>
