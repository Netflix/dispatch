<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer location="right" width="900">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title class="text-h6">
            {{ name }}
          </v-list-item-title>
          <v-list-item-subtitle>
            Reported - {{ formatRelativeDate(reported_at) }}
          </v-list-item-subtitle>

          <v-btn
            v-if="status == 'New' || status == 'Triage'"
            @click="showEscalateDialog(selected)"
            color="error"
          >
            <v-icon start> error_outline </v-icon>
            Escalate Case
          </v-btn>
          <v-spacer />
          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!isValid.value"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeEditSheet">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-tabs color="primary" fixed-tabs v-model="tab">
        <v-tab key="details"> Details </v-tab>
        <v-tab key="resources"> Resources </v-tab>
        <v-tab key="participants"> Participants </v-tab>
        <v-tab key="timeline"> Timeline </v-tab>
        <v-tab key="workflows"> Workflows </v-tab>
        <v-tab key="entities"> Entities </v-tab>
        <v-tab key="signals"> Signals </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item key="details">
          <case-details-tab />
        </v-tab-item>
        <v-tab-item key="resources">
          <case-resources-tab />
        </v-tab-item>
        <v-tab-item key="participants">
          <case-participants-tab />
        </v-tab-item>
        <v-tab-item key="timeline">
          <case-timeline-tab />
        </v-tab-item>
        <v-tab-item key="workflow_instances">
          <workflow-instance-tab v-model="workflow_instances" />
        </v-tab-item>
        <v-tab-item key="entities">
          <entities-tab
            :selected="selected"
            v-model="signal_instances"
            v-if="selected.signal_instances"
          />
        </v-tab-item>
        <v-tab-item key="signal_instances">
          <signal-instance-tab v-model="signal_instances" v-if="selected.signal_instances" />
        </v-tab-item>
      </v-tabs-items>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate } from "@/filters"

import CaseDetailsTab from "@/case/DetailsTab.vue"
import CaseParticipantsTab from "@/case/ParticipantsTab.vue"
import CaseResourcesTab from "@/case/ResourcesTab.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"
import WorkflowInstanceTab from "@/workflow/WorkflowInstanceTab.vue"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"

export default {
  name: "CaseEditSheet",

  components: {
    CaseDetailsTab,
    CaseResourcesTab,
    CaseParticipantsTab,
    CaseTimelineTab,
    WorkflowInstanceTab,
    SignalInstanceTab,
    EntitiesTab,
  },

  data() {
    return {
      tab: null,
    }
  },

  setup() {
    return { formatRelativeDate }
  },

  computed: {
    ...mapFields("case_management", [
      "selected",
      "selected.id",
      "selected.name",
      "selected.project",
      "selected.reported_at",
      "selected.status",
      "selected.loading",
      "selected.signal_instances",
      "selected.workflow_instances",
      "dialogs.showEditSheet",
    ]),
  },

  created() {
    this.fetchDetails()
  },

  watch: {
    "$route.params.name": function () {
      this.fetchDetails()
    },
  },

  methods: {
    fetchDetails() {
      this.getDetails({ name: this.$route.params.name })
    },
    ...mapActions("case_management", [
      "save",
      "getDetails",
      "closeEditSheet",
      "showEscalateDialog",
    ]),
  },
}
</script>
