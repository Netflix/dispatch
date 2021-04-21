<template>
  <div>
    <v-data-table :headers="headers" :items="items" :loading="loading" hide-default-footer>
      <template v-slot:item.incident_priority.name="{ item }">
        <incident-priority :priority="item.incident_priority.name" />
      </template>
      <template v-slot:item.status="{ item }">
        <incident-status :status="item.status" :id="item.id" />
      </template>
      <template v-slot:item.commander="{ item }">
        <incident-participant :participant="item.commander" />
      </template>
      <template v-slot:item.reporter="{ item }">
        <incident-participant :participant="item.reporter" />
      </template>
      <template v-slot:item.reported_at="{ item }">
        {{ item.reported_at | formatDate }}
      </template>
      <template v-slot:item.data-table-actions="{ item }">
        <v-menu bottom left>
          <template v-slot:activator="{ on }">
            <v-btn icon v-on="on">
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item :to="{ name: 'IncidentTableEdit', params: { name: item.name } }">
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

import IncidentPriority from "@/incident/IncidentPriority.vue"
import IncidentStatus from "@/incident/IncidentStatus"
import IncidentParticipant from "@/incident/Participant.vue"

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
        { text: "Name", value: "name", align: "left", width: "10%" },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status" },
        { text: "Type", value: "incident_type.name" },
        //{ text: "Priority", value: "incident_priority.name", width: "10%" },
        { text: "Commander", value: "commander", sortable: false },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
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
