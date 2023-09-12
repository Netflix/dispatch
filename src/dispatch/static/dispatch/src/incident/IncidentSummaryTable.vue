<template>
  <v-data-table hover :headers="headers" :items="items" :loading="loading">
    <template #item.incident_priority.name="{ item }">
      <incident-priority :priority="item.raw.incident_priority.name" />
    </template>
    <template #item.status="{ item }">
      <incident-status :status="item.raw.status" :id="item.raw.id" />
    </template>
    <template #item.commander="{ item }">
      <incident-participant :participant="item.raw.commander" />
    </template>
    <template #item.reporter="{ item }">
      <incident-participant :participant="item.raw.reporter" />
    </template>
    <template #item.project.name="{ item }">
      <v-chip small :color="item.raw.project.color">
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
      <v-menu location="bottom left">
        <template #activator="{ props }">
          <v-btn icon="mdi-dots-vertical" variant="text" density="comfortable" v-bind="props" />
        </template>
        <v-list>
          <v-list-item :to="{ name: 'IncidentTableEdit', params: { name: item.raw.name } }">
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
