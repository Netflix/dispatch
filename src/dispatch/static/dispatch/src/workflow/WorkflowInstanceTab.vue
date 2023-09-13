<template>
  <v-data-table
    :headers="headers"
    :items="value"
    :items-per-page="-1"
    disabled-pagination
    hide-default-footer
  >
    <template #item.parameters="{ item }">
      <workflow-instance-detail-menu :value="item" />
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
import { formatRelativeDate, formatDate } from "@/filters"

import WorkflowInstanceDetailMenu from "@/workflow/WorkflowInstanceDetailMenu.vue"

export default {
  name: "WorkflowInstanceTab",
  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
  },
  components: {
    WorkflowInstanceDetailMenu,
  },
  data() {
    return {
      menu: false,
      headers: [
        { text: "Name", value: "workflow.name" },
        { text: "Status", value: "status" },
        { text: "Creator", value: "creator.individual.name" },
        { text: "Run Reason", value: "run_reason" },
        { text: "Created At", value: "created_at" },
        { text: "", value: "parameters" },
      ],
    }
  },
  setup() {
    return { formatRelativeDate, formatDate }
  },
}
</script>
