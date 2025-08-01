<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer
      location="right"
      :width="navigation.width"
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
              v-if="status == 'New' || status == 'Triage'"
              @click="showEscalateDialog(selected)"
              color="error"
              prepend-icon="mdi-fire"
            >
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
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeEditSheet">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-tabs color="primary" fixed-tabs v-model="tab">
        <v-tab value="details"> Details </v-tab>
        <v-tab value="resources"> Resources </v-tab>
        <v-tab value="participants"> Participants </v-tab>
        <v-tab value="timeline"> Timeline </v-tab>
        <v-tab value="costs"> Cost </v-tab>
        <v-tab value="workflows"> Workflows </v-tab>
        <v-tab value="entities"> Entities </v-tab>
        <v-tab value="signals"> Signals </v-tab>
      </v-tabs>
      <v-window v-model="tab">
        <v-window-item value="details">
          <case-details-tab />
        </v-window-item>
        <v-window-item value="resources">
          <case-resources-tab />
        </v-window-item>
        <v-window-item value="participants">
          <case-participants-tab />
        </v-window-item>
        <v-window-item value="timeline">
          <case-timeline-tab-v1 />
        </v-window-item>
        <v-window-item value="costs">
          <case-costs-tab />
        </v-window-item>
        <v-window-item value="workflows">
          <workflow-instance-tab v-model="workflow_instances" />
        </v-window-item>
        <v-window-item value="entities">
          <entities-tab
            :selected="selected"
            v-model="signal_instances"
            v-if="selected.signal_instances"
          />
        </v-window-item>
        <v-window-item value="signals">
          <signal-instance-tab v-model="signal_instances" v-if="selected.signal_instances" />
        </v-window-item>
      </v-window>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate } from "@/filters"

import CaseCostsTab from "@/case/CostsTab.vue"
import CaseDetailsTab from "@/case/DetailsTab.vue"
import CaseParticipantsTab from "@/case/ParticipantsTab.vue"
import CaseResourcesTab from "@/case/ResourcesTab.vue"
import CaseTimelineTabV1 from "@/case/CaseTimelineTabV1.vue"
import WorkflowInstanceTab from "@/workflow/WorkflowInstanceTab.vue"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"

export default {
  name: "CaseEditSheet",

  components: {
    CaseCostsTab,
    CaseDetailsTab,
    CaseResourcesTab,
    CaseParticipantsTab,
    CaseTimelineTabV1,
    WorkflowInstanceTab,
    SignalInstanceTab,
    EntitiesTab,
  },

  data() {
    return {
      tab: null,
      navigation: {
        width: parseInt(localStorage.getItem("case-drawer-width")) || 900,
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
        if (newVal.meta?.showTimeline) {
          this.tab = "timeline"
        }
      },
    },
    "navigation.width": function (newWidth) {
      localStorage.setItem("case-drawer-width", newWidth.toString())
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
    ...mapActions("case_management", [
      "save",
      "getDetails",
      "closeEditSheet",
      "showEscalateDialog",
    ]),
  },
}
</script>
