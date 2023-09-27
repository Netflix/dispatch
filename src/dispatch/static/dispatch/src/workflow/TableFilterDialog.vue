<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Column Filters</span>
      </v-card-title>
      <v-list density="compact" />
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"
export default {
  name: "WorkflowTableFilterDialog",
  data() {
    return {
      display: false,
    }
  },
  computed: {
    ...mapFields("workflow", []),
    numFilters: function () {
      return sum([])
    },
  },
}
</script>
