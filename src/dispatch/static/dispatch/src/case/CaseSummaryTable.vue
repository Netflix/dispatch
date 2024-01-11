<template>
  <v-data-table :headers="headers" :items="items" :loading="loading">
    <template #item.case_priority.name="{ value }">
      <case-priority :priority="value" />
    </template>
    <template #item.status="{ item, value }">
      <case-status :status="value" :id="item.id" />
    </template>
    <template #item.project.name="{ item, value }">
      <v-chip size="small" :color="item.project.color">
        {{ value }}
      </v-chip>
    </template>
    <template #item.reported_at="{ value }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(value) }}</span>
        </template>
        <span>{{ formatDate(value) }}</span>
      </v-tooltip>
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item :to="{ name: 'CaseTableEdit', params: { name: item.name } }">
            <v-list-item-title>View / Edit</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-data-table>
</template>
<script>
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"
import CasePriority from "@/case/priority/CasePriority.vue"
import CaseStatus from "@/case/CaseStatus.vue"

export default {
  name: "CaseSummaryTable",

  components: {
    CasePriority,
    CaseStatus,
  },

  data() {
    return {
      headers: [
        { title: "Name", key: "name", align: "left", sortable: false, width: "10%" },
        { title: "Title", key: "title", sortable: false },
        { title: "Status", key: "status", sortable: false },
        { title: "Type", key: "case_type.name", sortable: false },
        { title: "Priority", key: "case_priority.name", sortable: false, width: "10%" },
        { title: "Project", key: "project.name", sortable: false },
        { title: "Reported At", key: "reported_at", sortable: false },
        { title: "Assignee", key: "assignee.email", sortable: false },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  props: {
    items: {
      default: function () {
        return []
      },
      type: Array,
    },
    loading: {
      default: function () {
        return false
      },
      type: [String, Boolean],
    },
  },

  methods: {
    ...mapActions("case", ["showEditSheet"]),
  },
}
</script>
