<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer
      location="right"
      :width="navigation.width"
      ref="drawer"
      :permanent="$vuetify.display.mdAndDown"
      :style="{ transition: isResizing ? 'none' : 'width 0.2s ease' }"
    >
      <div
        class="resize-handle"
        @mousedown="startResize"
        @mouseenter="handleHover = true"
        @mouseleave="handleHover = false"
        :style="{
          position: 'absolute',
          left: '0',
          top: '0',
          bottom: '0',
          width: '4px',
          cursor: 'ew-resize',
          background: handleHover ? '#ff0000' : 'transparent',
          zIndex: 1000,
          transition: 'background 0.2s ease',
        }"
      />
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title class="text-h6">
            {{ name }}
          </v-list-item-title>
          <v-list-item-subtitle>
            Reported - {{ formatRelativeDate(reported_at) }}
          </v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeEditSheet">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-tabs color="primary" fixed-tabs v-model="tab" :disabled="id == null">
        <v-tab value="details"> Details </v-tab>
        <v-tab value="reports"> Reports </v-tab>
        <v-tab value="resources"> Resources </v-tab>
        <v-tab value="participants"> Participants </v-tab>
        <v-tab value="timeline"> Timeline </v-tab>
        <v-tab value="tasks"> Tasks </v-tab>
        <v-tab value="costs"> Costs </v-tab>
        <v-tab value="forms"> Forms </v-tab>
        <v-tab value="workflows"> Workflows </v-tab>
      </v-tabs>
      <v-window v-model="tab">
        <v-window-item value="details">
          <incident-details-tab />
        </v-window-item>
        <v-window-item value="reports">
          <incident-timeline-report-tab />
        </v-window-item>
        <v-window-item value="resources">
          <incident-resources-tab />
        </v-window-item>
        <v-window-item value="participants">
          <incident-participants-tab />
        </v-window-item>
        <v-window-item value="timeline">
          <incident-timeline-tab />
        </v-window-item>
        <v-window-item value="tasks">
          <incident-tasks-tab />
        </v-window-item>
        <v-window-item value="costs">
          <incident-costs-tab />
        </v-window-item>
        <v-window-item value="forms">
          <incident-forms-tab />
        </v-window-item>
        <v-window-item value="workflow_instances">
          <workflow-instance-tab v-model="workflow_instances" />
        </v-window-item>
      </v-window>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate } from "@/filters"

import IncidentCostsTab from "@/incident/CostsTab.vue"
import IncidentDetailsTab from "@/incident/DetailsTab.vue"
import IncidentParticipantsTab from "@/incident/ParticipantsTab.vue"
import IncidentResourcesTab from "@/incident/ResourcesTab.vue"
import IncidentTimelineReportTab from "@/incident/TimelineReportTab.vue"
import IncidentTasksTab from "@/incident/TasksTab.vue"
import IncidentTimelineTab from "@/incident/TimelineTab.vue"
import WorkflowInstanceTab from "@/workflow/WorkflowInstanceTab.vue"
import IncidentFormsTab from "@/incident/FormsTab.vue"

export default {
  name: "IncidentEditSheet",

  components: {
    IncidentCostsTab,
    IncidentDetailsTab,
    IncidentParticipantsTab,
    IncidentResourcesTab,
    IncidentTimelineReportTab,
    IncidentTasksTab,
    IncidentTimelineTab,
    WorkflowInstanceTab,
    IncidentFormsTab,
  },

  data() {
    return {
      tab: null,
      navigation: {
        width: parseInt(localStorage.getItem("incident-drawer-width")) || 800,
        minWidth: 400,
        maxWidth: 1200,
      },
      isResizing: false,
      handleHover: false,
    }
  },

  setup() {
    return { formatRelativeDate }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.project",
      "selected.reported_at",
      "selected.loading",
      "selected.workflow_instances",
      "dialogs.showEditSheet",
    ]),
  },

  created() {
    this.fetchDetails()
  },

  mounted() {
    document.addEventListener("mousemove", this.onMouseMove)
    document.addEventListener("mouseup", this.onMouseUp)
  },

  beforeUnmount() {
    document.removeEventListener("mousemove", this.onMouseMove)
    document.removeEventListener("mouseup", this.onMouseUp)
  },

  watch: {
    "$route.params.name": function () {
      this.fetchDetails()
    },
    $route: {
      immediate: true,
      handler(newVal) {
        if (!newVal.meta) return
        if (newVal.meta.showTimeline) {
          this.tab = "timeline"
        } else if (newVal.meta.showForms) {
          this.tab = "forms"
        }
      },
    },
    "navigation.width": function (newWidth) {
      localStorage.setItem("incident-drawer-width", newWidth.toString())
    },
  },

  methods: {
    fetchDetails() {
      if (this.$route.params.name) {
        this.getDetails({ name: this.$route.params.name })
      }
    },
    startResize(e) {
      this.isResizing = true
      e.preventDefault()
    },
    onMouseMove(e) {
      if (!this.isResizing) return

      const newWidth = window.innerWidth - e.clientX
      if (newWidth >= this.navigation.minWidth && newWidth <= this.navigation.maxWidth) {
        this.navigation.width = newWidth
      }
    },
    onMouseUp() {
      this.isResizing = false
    },
    ...mapActions("incident", ["save", "getDetails", "closeEditSheet"]),
  },
}
</script>
