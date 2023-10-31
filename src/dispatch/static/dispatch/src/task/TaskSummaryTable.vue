<template>
  <new-edit-sheet />
  <v-data-table :headers="headers" :items="items" :loading="loading">
    <template #item.description="{ value }">
      <div class="text-truncate" style="max-width: 400px">
        {{ value }}
      </div>
    </template>
    <template #item.project.name="{ item, value }">
      <v-chip size="small" :color="item.project.color">
        {{ value }}
      </v-chip>
    </template>
    <template #item.incident_priority.name="{ value }">
      <incident-priority :priority="value" />
    </template>
    <template #item.creator="{ value }">
      <participant :participant="value" />
    </template>
    <template #item.owner="{ value }">
      <participant :participant="value" />
    </template>
    <template #item.incident_type.name="{ value }">
      {{ value }}
    </template>
    <template #item.assignees="{ value }">
      <participant v-for="assignee in value" :key="assignee.id" :participant="assignee" />
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="right" origin="overlap">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item @click="createEditShow(item)">
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

import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import NewEditSheet from "@/task/NewEditSheet.vue"
import Participant from "@/incident/Participant.vue"

export default {
  name: "TaskTable",

  components: {
    NewEditSheet,
    IncidentPriority,
    Participant,
  },
  data() {
    return {
      headers: [
        { title: "Incident Name", key: "incident.name", sortable: false },
        { title: "Status", key: "status", sortable: false },
        { title: "Creator", key: "creator", sortable: false },
        { title: "Owner", key: "owner", sortable: false },
        { title: "Assignees", key: "assignees", sortable: false },
        { title: "Description", key: "description", sortable: false },
        { title: "Project", key: "project.name", sortable: true },
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
    ...mapActions("task", ["createEditShow", "removeShow"]),
  },
}
</script>
