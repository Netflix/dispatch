<template>
  <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
          <v-list-item-title v-else class="title"> New </v-list-item-title>
          <v-list-item-subtitle>Incident Role Policy - {{ role }}</v-list-item-subtitle>
        </v-list-item-content>
        <v-btn icon color="info" :loading="loading" @click="save()">
          <v-icon>save</v-icon>
        </v-btn>
        <v-btn icon color="secondary" @click="closeCreateEdit()">
          <v-icon>close</v-icon>
        </v-btn>
      </v-list-item>
    </template>
    <v-card flat>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <span class="subtitle-2">Parameters</span>
            </v-flex>
            <v-flex xs12>
              <tag-filter-combobox label="Tags" :project="project" v-model="tags" />
            </v-flex>
            <v-flex xs12>
              <incident-priority-combobox :project="project" v-model="incident_priorities" />
            </v-flex>
            <v-flex xs12>
              <incident-type-combobox :project="project" v-model="incident_types" />
            </v-flex>
            <v-flex xs12>
              <span class="subtitle-2">Targets</span>
            </v-flex>
            <v-flex xs12>
              <service-select :project="project" v-model="service"></service-select>
            </v-flex>
            <v-flex xs12>
              <v-checkbox
                v-model="enabled"
                label="Enabled"
                hint="Check this if you would like this policy to be considered when resolving the role."
              />
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"

export default {
  name: "IncidentRoleNewEditSheet",

  components: {
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    TagFilterCombobox,
    ServiceSelect,
  },

  computed: {
    ...mapFields("incident_role", [
      "selected.incident_priorities",
      "selected.incident_types",
      "selected.role",
      "selected.tags",
      "selected.service",
      "selected.individual",
      "selected.enabled",
      "selected.id",
      "selected.project",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("incident_role", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
