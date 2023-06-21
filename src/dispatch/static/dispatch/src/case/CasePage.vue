<template>
  <v-container fluid class="pt-6">
    <v-row no-gutters align="center">
      <v-col>
        <v-breadcrumbs :items="breadcrumbItems">
          <template v-slot:divider>
            <v-icon>mdi-chevron-right</v-icon>
          </template>
        </v-breadcrumbs>

        <div class="pl-6 pt-2 headline-5 font-weight-medium">
          {{ _case.title }}
        </div>
        <div class="pl-6 pt-2 subtitle font-weight-light">
          <v-chip outlined small class="mr-2" :color="getPriorityColor(_case.case_priority)">
            <v-icon dense small class="pr-2" :color="getPriorityColor(_case.case_priority)">
              mdi-alert-plus-outline
            </v-icon>
            {{ _case.case_priority.name }}
          </v-chip>
          <span v-if="!fullText"> {{ trimmedDescription }} </span>
          <span v-else> {{ _case.description }} </span>
          <v-btn
            x-small
            text
            elevation="0"
            color="black"
            @click="toggleText"
            v-if="_case.description.length > 100"
          >
            <span color="black"> {{ fullText ? "Show Less" : "..." }} </span>
          </v-btn>
        </div>
      </v-col>
      <v-col cols="auto">
        <v-btn outlined small elevation="1" color="secondary" class="mr-1 ml-2"
          ><v-icon small>mdi-dots-horizontal </v-icon></v-btn
        >
        <v-btn outlined small color="secondary" elevation="1" class="ml-1"
          ><v-icon small>mdi-bell-off</v-icon></v-btn
        >
        <v-btn outlined small color="primary" elevation="1" class="mr-4 ml-2"
          ><v-icon small class="mr-1">mdi-fire</v-icon>Escalate</v-btn
        >
      </v-col>
    </v-row>
    <v-divider class="mt-6 mb-6"></v-divider>
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
              <v-icon dense small class="pr-2"> mdi-broadcast </v-icon> Investigate
            </v-tab>
            <v-tab key="entities" class="tab rounded-b-0 rounded-lg">
              <v-icon dense small class="pr-2"> mdi-account-group </v-icon> Entities
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="tab">
            <v-tab-item key="main" class="tab">
              <div>
                <!-- <rich-resolution></rich-resolution> -->
                <CaseTimelineAdvanced></CaseTimelineAdvanced>
                <!-- <CaseTimeline :events="_case.events" :caseName="_case.name" /> -->
              </div>
            </v-tab-item>
            <v-tab-item key="signals" class="tab">
              <signal-instance-card-viewer :caseId="_case.id" />
              <v-divider></v-divider>
              <entities-tab :selected="_case" v-model="signal_instances" />
            </v-tab-item>
            <v-tab-item key="entities">
              <entities-tab :selected="_case" v-model="signal_instances" />
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
      <v-divider vertical></v-divider>
      <v-col cols="3">
        <v-card class="px-6 pt-6 pb-6 mr-4" elevation="0">
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6 subtitle-2">
                <v-icon dense small color="black lighten-1" class="mr-2"> mdi-account </v-icon
                >Assignee
              </div>
            </v-col>
            <v-col cols="auto">
              <new-participant-select :project="_case.project" :participant="_case.assignee" />
            </v-col>
          </v-row>
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6 subtitle-2">
                <v-icon dense small color="black lighten-1" class="mr-2"> mdi-account </v-icon
                >Reporter
              </div>
            </v-col>
            <v-col cols="auto">
              <new-participant-select
                :project="_case.project"
                :label="Reporter"
                :participant="_case.assignee"
              />
            </v-col>
          </v-row>
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6 subtitle font-weight-light">Status</div>
            </v-col>
            <v-col cols="auto">
              <v-select
                v-model="_case.status"
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
              <!-- <v-chip outlined small class="mr-2" :color="getPriorityColor(_case.case_priority)">
                <v-icon dense small class="pr-2" :color="getPriorityColor(_case.case_priority)">
                  mdi-alert-plus-outline
                </v-icon>
                {{ _case.case_priority.name }}
              </v-chip> -->
              <new-case-priority-select v-model="_case.case_priority" :project="_case.project" />
            </v-col>
          </v-row>
          <div>
            <v-textarea outlined name="input-7-4" label="Resolution" value=""></v-textarea>
            <rich-resolution></rich-resolution>
          </div>
          <v-divider class="mt-6 mb-6"></v-divider>

          <v-row no-gutters justify="space-between" align="center" class="pb-6">
            <v-col cols="auto">
              <div class="subtitle font-weight-light">
                <v-icon dense small class="mr-2 subtitle font-weight-light">
                  mdi-calendar-clock
                </v-icon>
                Created
              </div>
            </v-col>
            <v-col cols="auto">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on" class="wavy-underline">{{
                    _case.created_at | formatRelativeDate
                  }}</span>
                </template>
                <div v-html="formatToTimeZones(_case.created_at)"></div>
              </v-tooltip>
            </v-col>
          </v-row>

          <v-row no-gutters justify="space-between" align="center" class="pb-6">
            <v-col cols="auto">
              <div class="subtitle font-weight-light">
                <v-icon dense small class="mr-2"> mdi-timer-sand </v-icon>Triaged
              </div>
            </v-col>
            <v-col cols="auto">
              <div>{{ _case.triage_at | formatRelativeDate }}</div>
            </v-col>
          </v-row>

          <v-row no-gutters justify="space-between" align="center" class="pb-6">
            <v-col cols="auto">
              <div class="subtitle font-weight-light">
                <v-icon dense small class="mr-2" color="green"> mdi-check-all </v-icon>Resolved
              </div>
            </v-col>
            <v-col cols="auto">
              <div>{{ _case.closed_at | formatRelativeDate }}</div>
            </v-col>
          </v-row>

          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="subtitle font-weight-light">
                <v-icon dense small class="mr-2" color="red"> mdi-fire </v-icon>Escalated
              </div>
            </v-col>
            <v-col cols="auto">
              <div>{{ _case.escalated_at | formatRelativeDate }}</div>
            </v-col>
          </v-row>
          <!-- <v-divider class="mt-6 mb-6"></v-divider>

          <CaseTimeline :events="_case.events" :caseName="_case.name" /> -->
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import moment from "moment-timezone"

import CaseTimelineAdvanced from "@/case/CaseTimelineAdvanced.vue"
import CaseTimeline from "@/case/CaseTimeline.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"
import NewParticipant from "@/case/NewParticipant.vue"
import NewParticipantSelect from "@/case/NewParticipantSelect.vue"
import NewCasePrioritySelect from "@/case/priority/NewCasePrioritySelect.vue"
import RichResolution from "@/case/RichResolution.vue"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"
import SignalInstanceCardViewer from "@/signal/SignalInstanceCardViewer.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"

export default {
  name: "CasePage",

  components: {
    CaseTimelineAdvanced,
    CaseTimeline,
    CaseTimelineTab,
    NewParticipant,
    NewParticipantSelect,
    NewCasePrioritySelect,
    RichResolution,
    SignalInstanceTab,
    SignalInstanceCardViewer,
    EntitiesTab,
  },

  props: {
    _case: {
      type: Object,
      required: true,
      default: () => ({}), // returns an empty object if _case is not provided
    },
  },

  data() {
    return {
      tab: null,
      statuses: ["New", "Triage", "Escalated", "Closed"],
      fullText: false,
    }
  },

  computed: {
    breadcrumbItems() {
      return [
        {
          text: "Cases",
          disabled: false,
          href: `/${this.$route.params.organization}/cases`,
        },
        {
          text: this._case.name,
          disabled: true,
        },
      ]
    },
    trimmedDescription() {
      return this._case.description.length > 120
        ? this._case.description.slice(0, 120)
        : this._case.description
    },
  },

  methods: {
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
  text-decoration-style: wavy;
  text-decoration-color: lightgray;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}

.v-tooltip__content {
  background-color: rgba(211, 211, 211, 0.8) !important; /* lightgrey with 80% opacity */
  color: black !important;
  border: 1px dotted black !important;
}
</style>
