<template>
  <v-data-table
    :headers="headers"
    :items="value"
    :items-per-page="-1"
    disabled-pagination
    hide-default-footer
  >
    <template v-slot:item.parameters="{ item }">
      <workflow-instance-detail-menu :value="item" />
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
        { text: "Creator", value: "creator" },
        { text: "Run Reason", value: "run_reason" },
        { text: "Created At", value: "created_at" },
        { text: "", value: "parameters" },
      ],
    }
  },
}
</script>
