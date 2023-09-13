<template>
  <new-edit-sheet />
  <v-data-table :headers="headers" :items="items" :loading="loading">
    <template #item.description="{ item }">
      <div class="text-truncate" style="max-width: 400px">
        {{ item.raw.description }}
      </div>
    </template>
    <template #item.project.name="{ item }">
      <v-chip size="small" :color="item.project.color">
        {{ item.raw.project.name }}
      </v-chip>
    </template>
    <template #item.incident_priority.name="{ item }">
      <incident-priority :priority="item.raw.incident.incident_priority.name" />
    </template>
    <template #item.creator.individual_contact.name="{ item }">
      <participant :participant="item.raw.creator" />
    </template>
    <template #item.owner.individual_contact.name="{ item }">
      <participant :participant="item.raw.owner" />
    </template>
    <template #item.incident_type.name="{ item }">
      {{ item.raw.incident.incident_type.name }}
    </template>
    <template #item.assignees="{ item }">
      <participant
        v-for="assignee in item.raw.assignees"
        :key="assignee.id"
        :participant="assignee"
      />
    </template>
    <template #item.resolve_by="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(item.raw.resolve_by) }}</span>
        </template>
        <span>{{ formatDate(item.raw.resolve_by) }}</span>
      </v-tooltip>
    </template>
    <template #item.created_at="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(item.raw.created_at) }}</span>
        </template>
        <span>{{ formatDate(item.raw.created_at) }}</span>
      </v-tooltip>
    </template>
    <template #item.resolved_at="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(item.raw.resolved_by) }}</span>
        </template>
        <span>{{ formatDate(item.raw.resolve_by) }}</span>
      </v-tooltip>
    </template>
    <template #item.source="{ item }">
      <a :href="item.weblink" target="_blank" style="text-decoration: none">
        {{ item.raw.source }}
        <v-icon size="small">mdi-open-in-new</v-icon>
      </a>
    </template>
    <template #item.data-table-actions="{ item }">
      <v-menu location="bottom left">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
        </template>
        <v-list>
          <v-list-item @click="createEditShow(item.raw)">
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
        { title: "Creator", key: "creator.individual_contact.name", sortable: false },
        { title: "Owner", key: "owner.individual_contact.name", sortable: false },
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
