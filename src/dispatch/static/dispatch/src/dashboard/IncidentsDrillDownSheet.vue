<template>
  <v-navigation-drawer v-model="show" app clipped right bottom width="500">
    <template v-slot:prepend>
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
import IncidentDrillDownTable from "@/dashboard/IncidentDrillDownTable.vue"

export default {
  name: "IncidentsDrillDownSheet",

  props: {
    items: {
      default: function () {
        return []
      },
      type: Array,
    },
    show: {
      default: function () {
        return false
      },
      type: Boolean,
    },
  },

  methods: {
    hideSheet: function () {
      this.$emit("close")
    },
  },

  components: {
    IncidentDrillDownTable,
  },
}
</script>
