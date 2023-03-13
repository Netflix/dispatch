<template>
  <v-data-table
    :headers="headers"
    :items="cases"
    :items-per-page="-1"
    disabled-pagination
    hide-default-footer
  >
    <template v-slot:item.case="{ item }">
      <case-popover v-model="item" />
    </template>
    <template v-slot:item.created_at="{ item }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
        </template>
        <span>{{ item.created_at | formatDate }}</span>
      </v-tooltip>
    </template>
  </v-data-table>
</template>

<script>
import { mapFields } from "vuex-map-fields"

import CasePopover from "@/case/CasePopover.vue"

export default {
  name: "CaseTab",
  components: {
    CasePopover,
  },
  props: {
    inputCases: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      menu: false,
      headers: [
        { text: "Case", value: "case", sortable: false },
        { text: "Priority", value: "case_priority.name", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Created At", value: "created_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  computed: {
    ...mapFields("case_management", ["selected.cases"]),
    cases() {
      if (this.inputCases.length) {
        return this.inputCases
      }
      return this.case
    },
  },
}
</script>
