<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Signal Instance Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <signal-definition-combobox v-model="local_signal" label="Signal Definitions" />
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" variant="text" @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"

import SignalDefinitionCombobox from "@/signal/SignalDefinitionCombobox.vue"

export default {
  name: "SignalInstanceTableFilterDialog",

  components: {
    SignalDefinitionCombobox,
  },

  data() {
    return {
      display: false,
      local_signal: [],
    }
  },

  computed: {
    ...mapFields("signal", ["instanceTable.options.filters.signal"]),
    numFilters: function () {
      return sum([this.signal.length])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.signal = this.local_signal

      // we close the dialog
      this.display = false
    },
  },
}
</script>
