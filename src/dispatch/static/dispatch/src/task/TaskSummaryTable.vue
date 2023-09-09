<template>
  <div>
    <new-edit-sheet />
    <v-data-table :headers="headers" :items="items" :loading="loading">
      <template #item.description="{ item }">
        <div class="text-truncate" style="max-width: 400px">
          {{ item.description }}
        </div>
      </template>
      <template #item.project.name="{ item }">
        <v-chip small :color="item.project.color" text-color="white">
          {{ item.project.name }}
        </v-chip>
      </template>
      <template #item.incident_priority.name="{ item }">
        <incident-priority :priority="item.incident.incident_priority.name" />
      </template>
      <template #item.creator.individual_contact.name="{ item }">
        <participant :participant="item.creator" />
      </template>
      <template #item.owner.individual_contact.name="{ item }">
        <participant :participant="item.owner" />
      </template>
      <template #item.incident_type.name="{ item }">
        {{ item.incident.incident_type.name }}
      </template>
      <template #item.assignees="{ item }">
        <participant
          v-for="assignee in item.assignees"
          :key="assignee.id"
          :participant="assignee"
        />
      </template>
      <template #item.resolve_by="{ item }">
        <v-tooltip location="bottom">
          <template #activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ formatRelativeDate(item.resolve_by) }}</span>
          </template>
          <span>{{ formatDate(item.resolve_by) }}</span>
        </v-tooltip>
      </template>
      <template #item.created_at="{ item }">
        <v-tooltip location="bottom">
          <template #activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ formatRelativeDate(item.created_at) }}</span>
          </template>
          <span>{{ formatDate(item.created_at) }}</span>
        </v-tooltip>
      </template>
      <template #item.resolved_at="{ item }">
        <v-tooltip location="bottom">
          <template #activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ formatRelativeDate(item.resolved_by) }}</span>
          </template>
          <span>{{ formatDate(item.resolve_by) }}</span>
        </v-tooltip>
      </template>
      <template #item.source="{ item }">
        <a :href="item.weblink" target="_blank" style="text-decoration: none">
          {{ item.source }}
          <v-icon size="small">open_in_new</v-icon>
        </a>
      </template>
      <template #item.data-table-actions="{ item }">
        <v-menu location="bottom left">
          <template #activator="{ on }">
            <v-btn icon variant="text" v-on="on">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="createEditShow(item)">
              <v-list-item-title>View / Edit</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
  </div>
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
        { text: "Incident Name", value: "incident.name", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Creator", value: "creator.individual_contact.name", sortable: false },
        { text: "Owner", value: "owner.individual_contact.name", sortable: false },
        { text: "Assignees", value: "assignees", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Project", value: "project.name", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
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
