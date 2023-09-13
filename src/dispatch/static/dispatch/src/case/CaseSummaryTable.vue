<template>
  <v-data-table :headers="headers" :items="items" :loading="loading">
    <template #item.case_priority.name="{ item }">
      <case-priority :priority="item.raw.case_priority.name" />
    </template>
    <template #item.status="{ item }">
      <case-status :status="item.raw.status" :id="item.raw.id" />
    </template>
    <template #item.project.name="{ item }">
      <v-chip size="small" :color="item.raw.project.color">
        {{ item.raw.project.name }}
      </v-chip>
    </template>
    <template #item.reported_at="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(item.raw.reported_at) }}</span>
        </template>
        <span>{{ formatDate(item.raw.reported_at) }}</span>
      </v-tooltip>
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item :to="{ name: 'CaseTableEdit', params: { name: item.raw.name } }">
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
