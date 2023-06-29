<template>
  <v-container fluid class="pt-6" style="width: 1920px">
    <v-row no-gutters align="center">
      <v-col>
        <v-breadcrumbs class="ml-n6" :items="breadcrumbItems">
          <template v-slot:divider>
            <v-icon>mdi-chevron-right</v-icon>
          </template>
        </v-breadcrumbs>

        <div class="pt-2 headline font-weight-medium">
          {{ selected.title }}
        </div>
        <div class="pt-2 subtitle font-weight-light">
          <v-chip outlined small class="mr-2" :color="getPriorityColor(selected.case_priority)">
            <v-icon dense small class="pr-2" :color="getPriorityColor(selected.case_priority)">
              mdi-alert-plus-outline
            </v-icon>
            <b>{{ selected.case_priority.name }}</b>
          </v-chip>
          <span v-if="!fullText"> {{ trimmedDescription }} </span>
          <span v-else> {{ selected.description }} </span>
          <v-btn
            x-small
            text
            elevation="0"
            color="black"
            @click="toggleText"
            v-if="selected.description.length > 100"
          >
            <span color="black"> {{ fullText ? "Show Less" : "..." }} </span>
          </v-btn>
        </div>
      </v-col>
      <v-col class="d-flex flex-column align-end">
        <div class="pr-6">
          <participant-chips :participants="selected.participants"></participant-chips>
        </div>
        <div class="pt-11">
          <v-btn outlined small elevation="1" color="secondary" class="mr-1 ml-2">
            <v-icon small>mdi-dots-horizontal </v-icon>
          </v-btn>
          <v-btn outlined small color="secondary" elevation="1" class="ml-1 mr-2">
            <v-icon small>mdi-bell-off</v-icon>
          </v-btn>
          <v-btn
            outlined
            small
            color="primary"
            elevation="1"
            class="mr-4"
            @click="showEscalateDialog(selected)"
          >
            <v-icon small class="mr-1">mdi-fire</v-icon>Escalate
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <div>
      <!-- other elements... -->
      <escalate-dialog />
    </div>
    <v-divider class="mt-6"></v-divider>
    <v-card flat>
      <v-card-text>
        <v-row class="pt-4 pb-4" justify="left" align="center">
          <v-btn-toggle v-model="toggle_exclusive" mandatory rounded>
            <v-btn small> New </v-btn>
            <v-btn small> Triaged </v-btn>
            <v-btn small> Resolved </v-btn>
            <v-btn small> Escalated </v-btn>
          </v-btn-toggle>
          <!-- <v-chip class="ml-6" small color="grey lighten-2" text-color="black">
            Open for {{ openTime }}
          </v-chip> -->
          <v-chip class="ml-6" small text-color="black">
            {{ selected.case_type.name }}
          </v-chip>
        </v-row>
      </v-card-text>
    </v-card>
    <v-row>
      <v-col cols="9">
        <v-card class="rounded-b-2 rounded-lg ml-0">
          <v-tabs
            v-model="tab"
            class="rounded-b-0 rounded-lg"
            background-color="grey lighten-4"
            hide-slider
          >
            <v-tab key="main" class="tab rounded-b-0 rounded-lg custom-tab-text">
              <v-icon dense small> mdi-cube </v-icon>
            </v-tab>
            <v-tab key="signals" class="tab rounded-b-0 rounded-lg custom-tab-text">
              <v-icon dense small class="pr-2"> mdi-broadcast </v-icon> Signals
            </v-tab>
            <v-tab key="entities" class="tab rounded-b-0 rounded-lg">
              <v-icon dense small class="pr-2"> mdi-account-group </v-icon> Entities
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="tab">
            <v-tab-item key="main" class="tab">
              <div class="pt-12 pb-12 pr-12 pl-12">
                <v-card elevation="0" class="rounded-lg">
                  <v-card-title>
                    <v-icon class="mr-2">mdi-chart-timeline-variant </v-icon>Case Timeline </v-card-title
                  ><CaseTimeline class="pl-8 mr-4" />
                </v-card>
                <!-- <rich-resolution></rich-resolution> -->
              </div>
            </v-tab-item>
            <v-tab-item key="signals" class="tab">
              <signal-instance-card-viewer :caseId="selected.id" />
            </v-tab-item>
            <v-tab-item key="entities">
              <entities-tab :selected="selected" v-model="signal_instances" />
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
      <!-- <v-divider vertical></v-divider> -->
      <v-col cols="3">
        <v-card class="px-6 pt-6 pb-6 mr-4 rounded-lg" elevation="1" color="grey lighten-5">
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6 subtitle font-weight-medium">Assignee</div>
            </v-col>
            <v-col cols="auto">
              <new-participant-select :project="selected.project" :value="selected.assignee" />
            </v-col>
          </v-row>
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6 subtitle font-weight-medium">Reporter</div>
            </v-col>
            <v-col cols="auto">
              <new-participant-select :project="selected.project" :value="selected.reporter" />
            </v-col>
          </v-row>
          <!-- <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6 subtitle font-weight-light">Status</div>
            </v-col>
            <v-col cols="auto">
              <v-select
                v-model="selected.status"
                label="Status"
                :items="statuses"
                hint="The status of the case."
              />
            </v-col>
          </v-row>
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6 subtitle font-weight-light">Priority</div>
            </v-col>
            <v-col cols="auto">
              <new-case-priority-select
                v-model="selected.case_priority"
                :project="selected.project"
              />
            </v-col>
          </v-row> -->
          <!-- <div>
            <v-textarea outlined name="input-7-4" label="Resolution" value=""></v-textarea>
            <rich-resolution></rich-resolution>
          </div> -->
          <!-- <v-divider class="mb-6"></v-divider>

          <v-row no-gutters justify="space-between" align="center" class="pb-2">
            <v-col cols="auto">
              <div class="subtitle">
                <v-icon dense small class="mr-1 subtitle font-weight-light">
                  mdi-calendar-clock
                </v-icon>
                Created
              </div>
            </v-col>
            <v-col cols="auto">
              <v-tooltip right>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on" class="wavy-underline">{{
                    selected.created_at | formatRelativeDate
                  }}</span>
                </template>
                <div v-html="formatToTimeZones(selected.created_at)"></div>
              </v-tooltip>
            </v-col>
          </v-row>

          <v-row no-gutters justify="space-between" align="center" class="pb-2">
            <v-col cols="auto">
              <div class="subtitle">
                <v-icon dense small class="mr-2"> mdi-timer-sand </v-icon>Triaged
              </div>
            </v-col>
            <v-col cols="auto">
              <v-tooltip right>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on" class="wavy-underline">{{
                    selected.triage_at | formatRelativeDate
                  }}</span>
                </template>
                <div v-html="formatToTimeZones(selected.triage_at)"></div>
              </v-tooltip>
            </v-col>
          </v-row>

          <v-row no-gutters justify="space-between" align="center" class="pb-2">
            <v-col cols="auto">
              <div class="subtitle">
                <v-icon dense small class="mr-2" color="green"> mdi-check-all </v-icon>Resolved
              </div>
            </v-col>
            <v-col cols="auto">
              <v-tooltip right>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on" class="wavy-underline">{{
                    selected.closed_at | formatRelativeDate
                  }}</span>
                </template>
                <div v-html="formatToTimeZones(selected.closed_at)"></div>
              </v-tooltip>
            </v-col>
          </v-row>

          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="subtitle">
                <v-icon dense small class="mr-2" color="red"> mdi-fire </v-icon>Escalated
              </div>
            </v-col>
            <v-col cols="auto">
              <v-tooltip right>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on" class="wavy-underline">{{
                    selected.escalated_at | formatRelativeDate
                  }}</span>
                </template>
                <div v-html="formatToTimeZones(selected.escalated_at)"></div>
              </v-tooltip>
            </v-col>
          </v-row>
 -->
          <!-- <v-divider class="mt-6 mb-6"></v-divider> -->
          <v-card outlined class="rounded-lg">
            <v-textarea
              full-width
              solo
              flat
              autogrow
              rows="16"
              placeholder="Document your findings and provide the rationale for any decisions you made as part of this investigation..."
            ></v-textarea>

            <v-row class="pb-2 pr-2 pl-2">
              <v-col cols="8" class="d-flex align-center">
                <v-menu offset-y bottom>
                  <template v-slot:activator="{ on }">
                    <v-chip v-on="on" outlined small> {{ currentReason }} </v-chip>
                  </template>

                  <v-list>
                    <v-list-item @click="onSelectReason('False Positive')">
                      <v-list-item-title>False Positive</v-list-item-title>
                    </v-list-item>

                    <v-list-item @click="onSelectReason('User Acknowledged')">
                      <v-list-item-title>User Acknowledged</v-list-item-title>
                    </v-list-item>

                    <v-list-item @click="onSelectReason('True Positive')">
                      <v-list-item-title>True Positive</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </v-col>

              <v-col cols="4" class="d-flex justify-end align-center">
                <v-btn outlined small color="black" elevation="0"> Submit </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </v-card>
        <div class="pt-8 pl-2 pr-2">
          <h4 class="mb-2">Tags</h4>
          <v-chip-group active-class="primary--text" column>
            <v-chip flat close small v-for="tag in selected.tags" :key="tag">
              {{ tag }}
            </v-chip>
            <v-chip flat small> Add tag<v-icon class="ml-1" small>mdi-plus </v-icon> </v-chip>
          </v-chip-group>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import moment from "moment-timezone"

import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import CaseTimelineAdvanced from "@/case/CaseTimelineAdvanced.vue"
import CaseTimeline from "@/case/CaseTimeline.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"
import EscalateDialog from "@/case/EscalateDialog.vue"

import NewParticipant from "@/case/NewParticipant.vue"
import NewParticipantSelect from "@/case/NewParticipantSelect.vue"
import NewCasePrioritySelect from "@/case/priority/NewCasePrioritySelect.vue"
import RichResolution from "@/case/RichResolution.vue"
import ParticipantChips from "@/case/ParticipantChips.vue"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"
import SignalInstanceCardViewer from "@/signal/SignalInstanceCardViewer.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"

export default {
  name: "CasePage",

  components: {
    EscalateDialog,
    CaseTimelineAdvanced,
    CaseTimeline,
    CaseTimelineTab,
    NewParticipant,
    NewParticipantSelect,
    NewCasePrioritySelect,
    ParticipantChips,
    RichResolution,
    SignalInstanceTab,
    SignalInstanceCardViewer,
    EntitiesTab,
  },

  props: {
    _case: {
      type: Object,
      required: false,
      default: () => ({}), // returns an empty object if _case is not provided
    },
  },

  data() {
    return {
      tab: null,
      statuses: ["New", "Triage", "Escalated", "Closed"],
      fullText: false,
      currentReason: "Resolution Reason",
    }
  },

  created() {
    this.fetchDetails()
  },

  watch: {
    "$route.params.name": function () {
      this.fetchDetails()
    },
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

    breadcrumbItems() {
      return [
        {
          text: "Cases",
          disabled: false,
          href: `/${this.$route.params.organization}/cases`,
        },
        {
          text: this.selected.name,
          disabled: true,
        },
      ]
    },

    trimmedDescription() {
      return this.selected.description.length > 120
        ? this.selected.description.slice(0, 120)
        : this.selected.description
    },

    openTime() {
      if (this.selected && this.selected.created_at) {
        return moment().from(this.selected.created_at, true)
      }
      return ""
    },
  },

  methods: {
    fetchDetails() {
      this.getDetails({ name: this.$route.params.name })
    },

    onSelectReason(reason) {
      this.currentReason = reason
      // other logic as necessary
    },

    ...mapActions("case_management", [
      "save",
      "getDetails",
      "closeEditSheet",
      "showEscalateDialog",
    ]),

    toggleText() {
      this.fullText = !this.fullText
    },

    getPriorityColor(priority) {
      if (priority) {
        switch (priority.name) {
          case "Low":
            return "green lighten-1"
          case "Medium":
            return "orange"
          case "High":
            return "red darken-2"
          case "Critical":
            return "red darken-4"
        }
      }
      return "red darken-2"
    },

    formatRelativeDate(date) {
      return moment(date).fromNow()
    },

    formatToTimeZones(date) {
      if (!date) return ""

      let m = moment(date)
      return `UTC: ${date}<br> PST: ${m
        .tz("America/Los_Angeles")
        .format("YYYY-MM-DD HH:mm:ss")}<br>EST: ${m
        .tz("America/New_York")
        .format("YYYY-MM-DD HH:mm:ss")}`
    },
  },
}
</script>

<style scoped>
.v-tabs .v-tab.v-tab--active {
  background: white;
  border: 1px solid #ccc;
  border-bottom: none;
  border-radius: 12px 12px 0 0;
}

.v-tab {
  text-transform: none !important;
  color: rgb(39, 39, 39) !important;
  font-weight: normal !important;
  letter-spacing: normal !important;
}

.tab {
  transition: all 0.2s ease;
}

.wavy-underline {
  text-decoration: underline;
  text-decoration-style: dotted;
  text-decoration-color: silver;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}

.v-tooltip__content {
  background-color: rgba(211, 211, 211, 0.8) !important; /* lightgrey with 80% opacity */
  color: black !important;
  border: 1px dotted black !important;
}
</style>
