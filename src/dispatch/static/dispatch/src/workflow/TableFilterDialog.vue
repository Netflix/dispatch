<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap :content="numFilters">
        <v-btn color="secondary" dark v-on="on">Filter Columns</v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Column Filters</span>
      </v-card-title>
      <v-list dense> </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"
export default {
  name: "WorkflowTableFilterDialog",
  components: {},
  data() {
    return {
      display: false
    }
  },
  computed: {
    ...mapFields("workflow", []),
    numFilters: function() {
      return sum([])
    }
  }
}
</script>
