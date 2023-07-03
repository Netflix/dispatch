<template>
  <v-container fluid class="pt-6" style="width: 1920px">
    <v-card elevation="0">
      <v-row no-gutters align="center">
        <v-col>
          <v-breadcrumbs class="ml-n4" :items="breadcrumbItems">
            <template v-slot:divider>
              <v-icon>mdi-chevron-right</v-icon>
            </template>
          </v-breadcrumbs>

          <div class="pt-2 pl-2 headline font-weight-medium">
            {{ selected.title }}
          </div>
          <div class="pt-2 subtitle font-weight-light">
            <v-row>
              <v-col cols="12" sm="12">
                <v-textarea
                  v-model="selected.description"
                  solo
                  flat
                  dense
                  auto-grow
                  rows="1"
                  background-color="white"
                  @keyup.enter="toggleEdit"
                  class="hover-outline ml-n1 pl-1 mb-4"
                >
                </v-textarea>
                <div class="pl-2">
                  <case-priority-select-chip :_case="selected" v-bind="attrs" v-on="on" />

                  <v-chip class="ml-2 mr-4" small text-color="black">
                    {{ selected.case_type.name }}
                  </v-chip>
                  <v-btn-toggle v-model="toggle_exclusive" mandatory rounded>
                    <v-btn small>
                      <v-icon dense x-small class="mr-1 subtitle font-weight-light"
                        >mdi-calendar-clock</v-icon
                      >
                      New
                    </v-btn>
                    <v-btn small>
                      <v-icon dense x-small class="mr-2"> mdi-timer-sand </v-icon> Triaged
                    </v-btn>
                    <v-btn small>
                      <v-icon dense x-small class="mr-2"> mdi-check-all </v-icon> Resolved
                    </v-btn>
                    <v-btn small> <v-icon x-small class="mr-1">mdi-fire</v-icon> Escalated </v-btn>
                  </v-btn-toggle>

                  <v-tabs v-model="tab" class="ml-n3 pt-6" background-color="transparent">
                    <v-tabs-slider color="rgb(9, 19, 40"></v-tabs-slider>

                    <v-tab key="main" class="tab custom-tab-text">
                      <v-icon dense small class="pr-2"> mdi-cube </v-icon>
                      Timeline
                    </v-tab>
                    <v-tab key="signals" class="tab custom-tab-text">
                      <v-icon dense small class="pr-2"> mdi-broadcast </v-icon>
                      <v-badge bordered inline content="6">Signals</v-badge>
                    </v-tab>
                    <v-tab key="entities" class="tab">
                      <v-icon dense small class="pr-2"> mdi-account-group </v-icon>
                      <v-badge bordered inline content="2">Entities</v-badge>
                    </v-tab>
                  </v-tabs>
                </div>
              </v-col>
            </v-row>
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
    </v-card>

    <div>
      <!-- other elements... -->
      <escalate-dialog />
    </div>

    <v-row>
      <v-col cols="9">
        <v-divider></v-divider>
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
      </v-col>
      <!-- <v-divider vertical></v-divider> -->
      <v-col cols="3" class="pt-16">
        <div class="sticky-col">
          <v-card
            class="px-6 pt-6 pb-6 mr-4 rounded-lg"
            elevation="3"
            outlined
            color="white lighten-5"
          >
            <span>Assignee</span>

            <v-row no-gutters align="center">
              <v-col cols="auto">
                <v-icon dense class="pr-2 pb-6"> mdi-account-check </v-icon>
              </v-col>
              <v-col cols="auto">
                <new-participant-select :project="selected.project" :value="selected.assignee" />
              </v-col>
            </v-row>
            <span>Reporter</span>
            <v-row no-gutters align="center">
              <v-col cols="auto">
                <v-icon dense class="pr-2 pb-6"> mdi-account </v-icon>
              </v-col>
              <v-col cols="auto">
                <new-participant-select :project="selected.project" :value="selected.reporter" />
              </v-col>
            </v-row>
            <!-- <v-row no-gutters justify="space-between" align="center">
              <v-col cols="auto">
                <div class="pb-6 subtitle font-weight-medium">Visibility</div>
              </v-col>
              <v-col cols="auto">
                <div class="pb-6 subtitle font-weight-light">{{ selected.visibility }}</div>
              </v-col>
            </v-row> -->
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
                v-model="selected.resolution"
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
                      <v-chip v-on="on" small>
                        <v-icon small left> mdi-label </v-icon>
                        {{
                          selected.resolution_reason
                            ? selected.resolution_reason
                            : "Select a reason"
                        }}
                      </v-chip>
                    </template>

                    <v-list>
                      <v-list-item
                        v-for="reason in resolutionReasons"
                        :key="reason"
                        @click="onSelectReason(reason)"
                      >
                        <v-list-item-title>{{ reason }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-col>

                <v-col cols="4" class="d-flex justify-end align-center">
                  <v-btn outlined small color="black" elevation="0" @click="onSubmit()">
                    Submit
                  </v-btn>
                </v-col>
              </v-row>
            </v-card>
          </v-card>
          <div class="pt-8 pl-2 pr-2">
            <h4 class="mb-2">Resources</h4>
            <v-row class="pt-2" no-gutters justify="space-between" align="center">
              <v-col cols="auto">
                <v-icon dense small class="pr-2"> mdi-slack </v-icon> Conversation
              </v-col>
              <v-col cols="auto"> </v-col>
            </v-row>
            <v-row class="pt-6" no-gutters justify="space-between" align="center">
              <v-col cols="auto">
                <v-icon dense small class="pr-2"> mdi-jira </v-icon> Ticket
              </v-col>
              <v-col cols="auto"> </v-col>
            </v-row>
            <v-row class="pt-6" no-gutters justify="space-between" align="center">
              <v-col cols="auto">
                <v-icon dense small class="pr-2"> mdi-file-document </v-icon> Document
              </v-col>
              <v-col cols="auto"> </v-col>
            </v-row>
            <v-row class="pt-6" no-gutters justify="space-between" align="center">
              <v-col cols="auto">
                <v-icon dense small class="pr-2"> mdi-folder-google-drive </v-icon> Storage
              </v-col>
              <v-col cols="auto"> </v-col>
            </v-row>
            <h4 class="mt-8 mb-2">Tags</h4>
            <!-- <v-chip-group active-class="primary--text" column>
            <v-chip flat close small v-for="tag in selected.tags" :key="tag">
              {{ tag }}
            </v-chip>
            <v-chip flat small> Add tag<v-icon class="ml-1" small>mdi-plus </v-icon> </v-chip>
          </v-chip-group> -->

            <tag-chips :_case="selected"></tag-chips>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import moment from "moment-timezone"

import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import CasePrioritySelectChip from "@/case//priority/CasePrioritySelectChip.vue"
import CaseTimelineAdvanced from "@/case/CaseTimelineAdvanced.vue"
import CaseTimeline from "@/case/CaseTimeline.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"
import TagChips from "@/case/TagChips.vue"
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
    CasePrioritySelectChip,
    NewParticipant,
    NewParticipantSelect,
    NewCasePrioritySelect,
    ParticipantChips,
    RichResolution,
    SignalInstanceTab,
    SignalInstanceCardViewer,
    EntitiesTab,
    TagChips,
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
      editing: false,
      statuses: ["New", "Triage", "Escalated", "Closed"],
      fullText: false,
      currentReason: "Resolution Reason",
      priorities: ["High", "Medium", "Low"],
      resolutionReasons: ["False Positive", "User Acknowledged", "Mitigated", "Escalated"],
      visibilities: ["Open", "Restricted"],
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

    onSubmit(resolution_reason, resolution) {
      this.save_page()
    },

    toggleEdit() {
      this.editing = !this.editing
      if (!this.editing) {
        // Save or do something with the description here.
      }
    },

    changePriority(priority) {
      this.selected.case_priority = priority // Update the selected priority.

      // Here, you may want to call an API to update the priority in the backend.
      // this.updateCasePriority(this.selected.case_priority);
    },

    onSelectReason(reason) {
      this.selected.resolution_reason = reason
      // other logic as necessary
    },

    ...mapActions("case_management", ["save", "getDetails", "save_page", "showEscalateDialog"]),

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
/* .v-tabs .v-tab.v-tab--active {
  background: white;
  border: 1px solid #ccc;
  border-bottom: none;
  border-radius: 12px 12px 0 0;
} */

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

.hover-outline:hover {
  border: 1px solid rgba(0, 0, 0, 0.87); /* Change color as per your requirement */
}

.sticky-col {
  position: sticky;
  top: 80px;
}
</style>
