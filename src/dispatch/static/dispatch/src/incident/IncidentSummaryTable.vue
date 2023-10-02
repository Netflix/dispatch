<template>
  <v-data-table hover :headers="headers" :items="items" :loading="loading">
    <template #item.incident_priority.name="{ value }">
      <incident-priority :priority="value" />
    </template>
    <template #item.status="{ item, value }">
      <incident-status :status="value" :id="item.id" />
    </template>
    <template #item.commander="{ value }">
      <incident-participant :participant="value" />
    </template>
    <template #item.reporter="{ value }">
      <incident-participant :participant="value" />
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
          <v-btn icon="mdi-dots-vertical" variant="text" density="comfortable" v-bind="props" />
        </template>
        <v-list>
          <v-list-item :to="{ name: 'IncidentTableEdit', params: { name: item.name } }">
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

import IncidentParticipant from "@/incident/Participant.vue"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import IncidentStatus from "@/incident/status/IncidentStatus.vue"

export default {
  name: "IncidentSummaryTable",

  components: {
    IncidentPriority,
    IncidentStatus,
    IncidentParticipant,
  },

  data() {
    return {
      headers: [
        { title: "Name", key: "name", align: "left", width: "10%" },
        { title: "Title", key: "title", sortable: false },
        { title: "Status", key: "status" },
        { title: "Type", key: "incident_type.name" },
        { title: "Priority", key: "incident_priority.name", width: "10%" },
        { title: "Project", key: "project.name", sortable: true },
        { title: "Commander", key: "commander", sortable: false },
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
    ...mapActions("incident", ["showEditSheet", "joinIncident"]),
  },
}
</script>
