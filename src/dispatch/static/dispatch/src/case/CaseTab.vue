<template>
  <v-data-table
    :headers="headers"
    :items="cases"
    :items-per-page="-1"
    disabled-pagination
    hide-default-footer
  >
    <template #item.case="{ item }">
      <case-popover :value="item" />
    </template>
    <template #item.created_at="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(item.created_at) }}</span>
        </template>
        <span>{{ formatDate(item.created_at) }}</span>
      </v-tooltip>
    </template>
  </v-data-table>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { formatRelativeDate, formatDate } from "@/filters"
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
        { title: "Case", key: "case", sortable: false },
        { title: "Priority", key: "case_priority.name", sortable: false },
        { title: "Status", key: "status", sortable: false },
        { title: "Created At", key: "created_at" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  setup() {
    return { formatRelativeDate, formatDate }
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
