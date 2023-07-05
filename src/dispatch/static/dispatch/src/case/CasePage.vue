<template>
  <v-container fluid class="pt-6" style="width: 1920px">
    <v-row no-gutters align="start">
      <v-col cols="9">
        <v-breadcrumbs class="ml-n1" :items="breadcrumbItems">
          <template v-slot:divider>
            <v-icon>mdi-chevron-right</v-icon>
          </template>
        </v-breadcrumbs>

        <v-row align="vertical">
          <v-col cols="auto" class="pl-4">
            <v-responsive :width="`${selected.title.length - 7}.5rem`">
              <v-text-field
                solo
                dense
                flat
                background-color="transparent"
                class="hover-outline headline font-weight-medium mr-1"
                v-model="selected.title"
                hide-details="auto"
              >
              </v-text-field>
            </v-responsive>
          </v-col>

          <v-col cols="auto" class="pt-5 ml-n5">
            <case-priority-select-chip :_case="selected" v-bind="attrs" v-on="on" />
          </v-col>
        </v-row>

        <div class="pt-2">
          <v-row>
            <v-col cols="12" sm="12">
              <div class="pt-2 mr-16 pr-16 subtitle font-weight-light">
                <v-textarea
                  v-model="selected.description"
                  solo
                  flat
                  dense
                  auto-grow
                  rows="1"
                  hide-details="auto"
                  background-color="transparent"
                  @keyup.enter="toggleEdit"
                  class="pl-1 mb-4 mr-16 pr-16 hover-outline"
                >
                </v-textarea>
              </div>

              <!-- <div class="pl-3">
                <v-row no-gutters align="center">
                  <v-col cols="auto">
                    <case-priority-select-chip :_case="selected" v-bind="attrs" v-on="on" />
                  </v-col>

                  <v-col cols="auto">
                    <v-chip class="ml-2" small text-color="black">
                      {{ selected.case_type.name }}
                    </v-chip>
                  </v-col>
                </v-row>
              </div> -->
              <div>
                <v-row no-gutters align="center">
                  <v-col cols="24">
                    <case-status-select-group :_case="selected"></case-status-select-group>
                  </v-col>
                </v-row>
              </div>

              <div class="pl-4">
                <v-tabs v-model="tab" class="ml-n3 pt-6" background-color="transparent">
                  <v-tabs-slider color="rgb(9, 19, 40"></v-tabs-slider>

                  <v-tab key="main" class="tab custom-tab-text">
                    <v-icon dense small class="pr-2"> mdi-cube </v-icon>
                    Timeline
                  </v-tab>
                  <v-tab key="signals" class="tab custom-tab-text">
                    <v-icon dense small class="pr-2"> mdi-broadcast </v-icon>
                    <v-badge bordered color="rgb(43, 51, 67)" inline :content="totalSignalInstances"
                      >Signals</v-badge
                    >
                  </v-tab>
                  <v-tab key="entities" class="tab">
                    <v-icon dense small class="pr-2"> mdi-account-group </v-icon>
                    <v-badge bordered color="rgb(43, 51, 67)" inline content="2">Entities</v-badge>
                  </v-tab>
                </v-tabs>
              </div>
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
          </v-row>
        </div>
      </v-col>

      <!-- <v-col cols="3">
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
      </v-col> -->
      <v-col cols="3">
        <div>
          <v-row no-gutters align="center" justify="end" class="ml-8 pl-16">
            <v-col cols="4" md="auto">
              <participant-chips
                :participants="selected.participants"
                :highlightedParticipants="[selected.assignee.individual.name]"
              ></participant-chips>
            </v-col>

            <v-col cols="4">
              <v-btn class="ml-2" icon @click="toggleVisibility()">
                <v-icon dense v-if="this.selected.visibility == 'Open'">mdi-lock-open</v-icon>
                <v-icon v-else>mdi-lock</v-icon>
              </v-btn>

              <v-dialog v-model="visibilityDialog" max-width="600">
                <v-card>
                  <v-card-title>Update Case Visibility</v-card-title>
                  <v-card-text
                    >Are you sure you want to change the case visibility from
                    <b>{{ this.selected.visibility }}</b> to <b>{{ newVisibility }}</b></v-card-text
                  >
                  <v-btn
                    class="ml-6 mb-4"
                    small
                    color="info"
                    elevation="1"
                    @click="changeVisibility(newVisibility)"
                  >
                    Submit
                  </v-btn>
                </v-card>
              </v-dialog>

              <!-- <v-btn icon>
                <v-icon dense>mdi-delete</v-icon>
              </v-btn> -->

              <v-btn icon>
                <v-icon dense>mdi-fire</v-icon>
              </v-btn>

              <v-menu offset-y>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn v-bind="attrs" v-on="on" icon>
                    <v-icon dense>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item> <v-icon left dense>mdi-delete</v-icon> Delete </v-list-item>
                  <v-list-item> <v-icon left dense>mdi-fire</v-icon> Escalate </v-list-item>
                </v-list>
              </v-menu>
            </v-col>
          </v-row>
          <v-card class="px-6 pb-6 mr-4 rounded-lg mt-8 refactoring-ui-shadow" outlined>
            <!-- <span><v-icon dense class="pr-2"> mdi-account-check </v-icon>Assignee</span> -->

            <!-- <v-row justify="end">
              <v-col cols="auto" class="pt-2">
                <v-icon dense class="pr-2"> mdi-cog-outline </v-icon>
              </v-col>
            </v-row> -->

            <v-row no-gutters align="center" class="pt-6">
              <v-col cols="4">
                <div class="subtitle-2">Assignee</div>
              </v-col>
              <v-col cols="8">
                <new-participant-select :project="selected.project" :value="selected.assignee" />
              </v-col>
            </v-row>

            <v-row no-gutters align="center" class="pt-5">
              <v-col cols="4">
                <div class="subtitle-2">Reporter</div>
              </v-col>
              <v-col cols="8">
                <new-participant-select :project="selected.project" :value="selected.reporter" />
              </v-col>
            </v-row>
            <!-- <span><v-icon dense class="pr-2"> mdi-account </v-icon>Reporter</span> -->

            <v-row no-gutters align="center" class="pt-6">
              <v-col cols="4">
                <div class="subtitle-2">Priority</div>
              </v-col>
              <v-col cols="8">
                <case-priority-select-chip :_case="selected" v-bind="attrs" v-on="on" />
              </v-col>
            </v-row>

            <v-row no-gutters align="center" class="pt-8">
              <v-col cols="4">
                <div class="subtitle-2">Severity</div>
              </v-col>
              <v-col cols="8">
                <case-priority-select-chip :_case="selected" v-bind="attrs" v-on="on" />
              </v-col>
            </v-row>

            <v-row no-gutters align="center" class="pt-8">
              <v-col cols="4">
                <div class="subtitle-2">Type</div>
              </v-col>

              <v-col cols="8">
                <v-chip small text-color="black" color="#edf2f7">
                  {{ selected.case_type.name }}
                </v-chip>
              </v-col>
            </v-row>

            <!-- <v-divider class="mt-9"></v-divider>

            <v-row no-gutters align="center" class="pt-2">
              <div class="subtitle-2 pr-14">Visibility</div>
              <v-switch v-model="switch2" color="rgb(43, 51, 67)" inset></v-switch>
              <v-icon dense class="ml-n1">mdi-lock</v-icon>
            </v-row>

            <v-divider class="mt-6 mb-6"></v-divider> -->
            <v-card flat color="grey lighten-5" class="rounded-lg mt-8 hover-outline">
              <rich-editor></rich-editor>

              <!-- <v-textarea
                v-model="selected.resolution"
                full-width
                solo
                flat
                autogrow
                rows="10"
                background-color="grey lighten-4"
                class="mb-4"
                placeholder="Document your findings and provide the rationale for any decisions you made as part of this investigation..."
              ></v-textarea> -->

              <v-row class="pb-2 pr-2 pl-2">
                <v-col cols="8" class="d-flex align-center">
                  <v-menu offset-y bottom>
                    <template v-slot:activator="{ on }">
                      <v-chip v-on="on" small color="grey lighten-2">
                        <v-icon small left> mdi-pencil </v-icon>
                        {{
                          selected.resolution_reason
                            ? selected.resolution_reason
                            : "Select a resolution reason"
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
                  <v-btn small class="lower-btn" color="info" elevation="1" @click="onSubmit()">
                    Submit
                  </v-btn>
                </v-col>
              </v-row>
            </v-card>
            <!-- <div class="pt-11">
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
            </div> -->
            <!-- <v-row align="center" class="pt-8">
              <v-divider></v-divider>
              <v-chip v-on="on" small color="grey lighten-4" @click="show = !show">
                Details
                <v-icon small>{{ show ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
              </v-chip>
              <v-divider></v-divider>
            </v-row> -->

            <v-row align="center" class="pt-8 pr-2" justify="end">
              <v-btn elevation="0" text @click="show = !show">
                <div class="caption lower-btn">Details</div>
                <v-icon small>{{ show ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
              </v-btn>
            </v-row>

            <v-expand-transition>
              <div v-show="show">
                <v-row no-gutters align="center" class="pb-2 pt-8">
                  <v-col cols="4">
                    <div class="subtitle-2">
                      <v-icon dense small class="mr-1 subtitle font-weight-light">
                        mdi-calendar-clock
                      </v-icon>
                      Created
                    </div>
                  </v-col>
                  <v-col cols="8">
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

                <v-row no-gutters align="center" class="pb-2 pt-4">
                  <v-col cols="4">
                    <div class="subtitle-2">
                      <v-icon dense small class="mr-2"> mdi-timer-sand </v-icon>Triaged
                    </div>
                  </v-col>
                  <v-col cols="8">
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

                <v-row no-gutters align="center" class="pb-2 pt-4">
                  <v-col cols="4">
                    <div class="subtitle-2">
                      <v-icon dense small class="mr-2" color="green"> mdi-check-all </v-icon
                      >Resolved
                    </div>
                  </v-col>
                  <v-col cols="8">
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

                <v-row no-gutters align="center" class="pt-4">
                  <v-col cols="4">
                    <div class="subtitle-2">
                      <v-icon dense small class="mr-2" color="red"> mdi-fire </v-icon>Escalated
                    </div>
                  </v-col>
                  <v-col cols="8">
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
              </div>
            </v-expand-transition>

            <v-expand-transition>
              <div v-show="show">
                <v-row align="center" class="pt-8 pb-4">
                  <v-divider></v-divider>
                  <v-chip v-on="on" small color="grey lighten-4"> Resources </v-chip>
                  <v-divider></v-divider>
                </v-row>
                <v-row class="pt-2" no-gutters justify="space-between" align="center">
                  <v-col cols="auto">
                    <div class="subtitle-2">
                      <v-icon dense small class="pr-2"> mdi-slack </v-icon> Conversation
                    </div>
                  </v-col>
                  <v-col cols="auto"> </v-col>
                </v-row>
                <v-row class="pt-6" no-gutters justify="space-between" align="center">
                  <v-col cols="auto">
                    <div class="subtitle-2">
                      <v-icon dense small class="pr-2"> mdi-jira </v-icon> Ticket
                    </div>
                  </v-col>
                  <v-col cols="auto"> </v-col>
                </v-row>
                <v-row class="pt-6" no-gutters justify="space-between" align="center">
                  <v-col cols="auto">
                    <div class="subtitle-2">
                      <v-icon dense small class="pr-2"> mdi-file-document </v-icon> Document
                    </div>
                  </v-col>
                  <v-col cols="auto"> </v-col>
                </v-row>
                <v-row class="pt-6" no-gutters justify="space-between" align="center">
                  <v-col cols="auto">
                    <div class="subtitle-2">
                      <v-icon dense small class="pr-2"> mdi-folder-google-drive </v-icon> Storage
                    </div>
                  </v-col>
                  <v-col cols="auto"> </v-col>
                </v-row>
              </div>
            </v-expand-transition>
          </v-card>
          <!-- <div class="pt-8 pl-2 pr-2">
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
            </v-row> -->
          <!-- <h4 class="mt-8 mb-2">Related Incidents</h4>
          <tag-chips class="pb-16" :_case="selected"></tag-chips>
          <h4 class="mt-8 mb-2">Duplicates</h4>
          <tag-chips class="pb-16" :_case="selected"></tag-chips> -->
          <h4 class="mt-8 mb-2">Tags</h4>
          <tag-chips class="pb-16" :_case="selected"></tag-chips>
        </div>
      </v-col>
    </v-row>

    <div>
      <!-- other elements... -->
      <escalate-dialog />
    </div>
  </v-container>
</template>

<script>
import moment from "moment-timezone"

import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import CaseStatusSelectGroup from "@/case/CaseStatusSelectGroup.vue"
import CasePrioritySelectChip from "@/case/priority/CasePrioritySelectChip.vue"
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
import RichEditor from "@/components/RichEditor.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"

export default {
  name: "CasePage",

  components: {
    EscalateDialog,
    CaseStatusSelectGroup,
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
    RichEditor,
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
      show: false,
      editing: false,
      visibilityDialog: false,
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

    totalSignalInstances() {
      return this.selected.signal_instances.length
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

    toggleVisibility() {
      const newVisibility = this.selected.visibility === "Open" ? "Restricted" : "Open"
      this.openVisibilityDialog(newVisibility)
    },

    openVisibilityDialog(newVisibility) {
      this.newVisibility = newVisibility
      this.visibilityDialog = true
    },

    changeVisibility(newVisibility) {
      this.visibilityDialog = false
      console.log(newVisibility)
      this.selected.visibility = newVisibility
      this.save_page()
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
.lower-btn {
  text-transform: none !important;
  /* color: rgb(39, 39, 39) !important; */
  font-weight: bold !important;
  letter-spacing: normal !important;
}
.v-tab {
  text-transform: initial; /* Keeping the text's original state */
  color: #272727; /* Slightly darker shade of gray for better contrast and readability */
  font-weight: 400; /* Normal text-weight */
  letter-spacing: normal;
  line-height: 1.5; /* Spacing for better readability */
  font-family: "Inter", sans-serif; /* A modern, readable typeface */
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
  background-color: rgba(211, 211, 211, 0.8) !important;
  color: black !important;
  border: 1px dotted black !important;
}

.hover-outline {
  border: 1px dashed transparent;
  border-radius: 0px;
}

.hover-outline:hover {
  border: 1px dashed rgba(148, 148, 148, 0.87);
  border-radius: 20px;
}
.refactoring-ui-shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sticky-col {
  position: sticky;
  top: 80px;
}

.arrow {
  clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%);
}

.overlap-card {
  margin-left: -15px;
}

.overlap-card:first-child {
  margin-left: 0;
}

.overlap-card:last-child {
  margin-right: -15px;
}
.hover-card {
  position: relative;
  z-index: 1;
}

.hover-card-two {
  position: relative;
  z-index: 2;
}

.hover-card-three {
  position: relative;
  z-index: 3;
}
</style>
