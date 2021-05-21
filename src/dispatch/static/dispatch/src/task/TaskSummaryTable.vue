<template>
  <div>
    <new-edit-sheet />
    <v-data-table :headers="headers" :items="items" :loading="loading" hide-default-footer>
      <template v-slot:item.description="{ item }">
        <div class="text-truncate" style="max-width: 400px">
          {{ item.description }}
        </div>
      </template>
      <template v-slot:item.project.name="{ item }">
        <v-chip small :color="item.project.color" text-color="white">
          {{ item.project.name }}
        </v-chip>
      </template>
      <template v-slot:item.incident_priority.name="{ item }">
        <incident-priority :priority="item.incident.incident_priority.name" />
      </template>
      <template v-slot:item.creator.individual_contact.name="{ item }">
        <participant :participant="item.creator" />
      </template>
      <template v-slot:item.owner.individual_contact.name="{ item }">
        <participant :participant="item.owner" />
      </template>
      <template v-slot:item.incident_type.name="{ item }">
        {{ item.incident.incident_type.name }}
      </template>
      <template v-slot:item.assignees="{ item }">
        <participant
          v-for="assignee in item.assignees"
          :key="assignee.id"
          :participant="assignee"
        />
      </template>
      <template v-slot:item.resolve_by="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ item.resolve_by | formatRelativeDate }}</span>
          </template>
          <span>{{ item.resolve_by | formatDate }}</span>
        </v-tooltip>
      </template>
      <template v-slot:item.created_at="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
          </template>
          <span>{{ item.created_at | formatDate }}</span>
        </v-tooltip>
      </template>
      <template v-slot:item.resolved_at="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ item.resolved_by | formatRelativeDate }}</span>
          </template>
          <span>{{ item.resolve_by | formatDate }}</span>
        </v-tooltip>
      </template>
      <template v-slot:item.source="{ item }">
        <a :href="item.weblink" target="_blank" style="text-decoration: none">
          {{ item.source }}
          <v-icon small>open_in_new</v-icon>
        </a>
      </template>
      <template v-slot:item.data-table-actions="{ item }">
        <v-menu bottom left>
          <template v-slot:activator="{ on }">
            <v-btn icon v-on="on">
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
import NewEditSheet from "@/task/NewEditSheet.vue"
import IncidentPriority from "@/incident/IncidentPriority.vue"
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
