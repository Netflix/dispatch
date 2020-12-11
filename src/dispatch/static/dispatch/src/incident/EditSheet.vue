<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showEditSheet" app clipped right width="800">
      <template v-slot:prepend>
        <v-card elevation="0">
          <v-toolbar color="primary">
            <v-toolbar-title>Edit/View - {{ name }}</v-toolbar-title>

            <v-spacer></v-spacer>

            <v-btn
              icon
              color="info"
              :loading="loading"
              :disabled="invalid || !validated"
              @click="save()"
            >
              <v-icon>save</v-icon>
            </v-btn>
            <v-btn icon color="secondary" @click="closeEditSheet()">
              <v-icon>close</v-icon>
            </v-btn>

            <template v-slot:extension>
              <v-tabs v-model="tab" align-with-title color="gray0">
                <v-tab key="details">Details</v-tab>
                <v-tab key="resources">Resources</v-tab>
                <v-tab key="participants">Participants</v-tab>
                <v-tab key="timeline">Timeline</v-tab>
                <v-tab key="workflows">Workflows</v-tab>
              </v-tabs>
            </template>
          </v-toolbar>
          <v-tabs-items v-model="tab">
            <v-tab-item key="details">
              <incident-details-tab />
            </v-tab-item>
            <v-tab-item key="resources">
              <incident-resources-tab />
            </v-tab-item>
            <v-tab-item key="participants">
              <incident-participants-tab />
            </v-tab-item>
            <v-tab-item key="timeline">
              <incident-timeline-tab />
            </v-tab-item>
            <v-tab-item key="workflow_instances">
              <incident-workflow-instance-tab />
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </template>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver } from "vee-validate"

import IncidentDetailsTab from "@/incident/DetailsTab.vue"
import IncidentResourcesTab from "@/incident/ResourcesTab.vue"
import IncidentParticipantsTab from "@/incident/ParticipantsTab.vue"
import IncidentTimelineTab from "@/incident/TimelineTab.vue"
import IncidentWorkflowInstanceTab from "@/incident/WorkflowInstanceTab.vue"

export default {
  name: "IncidentEditSheet",

  components: {
    ValidationObserver,
    IncidentDetailsTab,
    IncidentResourcesTab,
    IncidentParticipantsTab,
    IncidentTimelineTab,
    IncidentWorkflowInstanceTab
  },

  data() {
    return {
      tab: null
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.reported_at",
      "selected.loading",
      "dialogs.showEditSheet"
    ])
  },

  methods: {
    ...mapActions("incident", ["save", "closeEditSheet"])
  }
}
</script>
