<template>
  <v-container fluid class="pt-6" style="width: 1920px">
    <v-row no-gutters align="start">
      <v-col cols="9">
        <v-breadcrumbs class="ml-n1" :items="breadcrumbItems">
          <template v-slot:divider>
            <v-icon>mdi-chevron-right</v-icon>
          </template>
        </v-breadcrumbs>

        <v-row align="center">
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
          <!--
          <v-col cols="auto">
            <v-chip small text-color="black" color="#edf2f7">
              {{ selected.project.name }}
            </v-chip>
            <v-chip small text-color="black" color="#edf2f7" class="ml-4">
              {{ selected.case_type.name }}
            </v-chip>
          </v-col> -->
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
                  @input="autosave"
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
                  <v-col cols="6" md="9">
                    <case-status-select-group :_case="selected"></case-status-select-group>
                  </v-col>
                  <!-- <v-col cols="4" md="auto">
                    <v-chip
                      small
                      text-color="black"
                      color="#edf2f7"
                      class="ml-4 chip-hover-outline"
                    >
                      <v-icon dense small class="pr-2"> mdi-content-duplicate </v-icon>
                      Duplicates
                      <v-icon small right>mdi-plus</v-icon>
                    </v-chip>
                    <v-badge
                      bordered
                      overlap
                      color="rgb(43, 51, 67)"
                      content="2"
                      class="mr-2 mb-4 ml-1"
                    ></v-badge>

                    <v-chip
                      small
                      text-color="black"
                      color="#edf2f7"
                      class="ml-4 chip-hover-outline"
                    >
                      <v-icon dense small class="pr-2"> mdi-fire </v-icon>
                      Incidents
                      <v-icon small right>mdi-plus</v-icon>
                    </v-chip>
                    <v-badge
                      bordered
                      overlap
                      color="rgb(43, 51, 67)"
                      content="2"
                      class="mr-2 mb-4 ml-1"
                    ></v-badge>

                    <v-chip
                      small
                      text-color="black"
                      color="#edf2f7"
                      class="ml-4 chip-hover-outline"
                    >
                      <v-icon dense small class="pr-2"> mdi-animation </v-icon>
                      Related
                      <v-icon small right>mdi-plus</v-icon>
                    </v-chip>
                    <v-badge
                      bordered
                      overlap
                      color="rgb(43, 51, 67)"
                      content="2"
                      class="mr-2 mb-4 ml-1"
                    ></v-badge>
                    <v-chip
                      small
                      text-color="black"
                      color="#edf2f7"
                      class="ml-4 chip-hover-outline"
                    >
                      <v-icon dense small class="pr-2"> mdi-tag </v-icon>
                      Tags
                      <v-icon small right>mdi-plus</v-icon>
                    </v-chip>
                    <v-badge
                      bordered
                      overlap
                      color="rgb(43, 51, 67)"
                      content="2"
                      class="mr-2 mb-4 ml-1"
                    ></v-badge>
                  </v-col> -->
                </v-row>
              </div>

              <div class="pl-4">
                <v-tabs v-model="tab" class="ml-n3 pt-6" background-color="transparent">
                  <v-tabs-slider color="transparent"></v-tabs-slider>

                  <v-tab key="main" class="tab custom-tab-text">
                    <v-icon dense small class="pr-2"> mdi-clock-outline </v-icon>
                    Timeline
                  </v-tab>
                  <v-tab key="resources" class="tab custom-tab-text">
                    <v-icon dense small class="pr-2"> mdi-semantic-web </v-icon>
                    Resources
                  </v-tab>
                  <v-tab
                    key="signals"
                    class="tab custom-tab-text"
                    :disabled="signal_instances.length === 0"
                  >
                    <v-icon dense small class="pr-2"> mdi-broadcast </v-icon>
                    <template v-if="signal_instances.length > 0">
                      <v-badge color="rgb(43, 51, 67)" inline :content="totalSignalInstances">
                        Signals
                      </v-badge>
                    </template>
                    <template v-else> Signals </template>
                  </v-tab>
                  <v-tab key="entities" class="tab">
                    <v-icon dense small class="pr-2"> mdi-account-group </v-icon>
                    <v-badge bordered color="rgb(43, 51, 67)" inline content="2">Entities</v-badge>
                  </v-tab>
                </v-tabs>
              </div>
              <v-divider class="ml-2"></v-divider>
              <v-tabs-items v-model="tab">
                <v-tab-item key="main" class="tab">
                  <div class="pt-12 pb-12 pr-12 pl-12">
                    <v-card elevation="0" class="rounded-lg">
                      <CaseTimeline class="pl-8 mr-4" />
                    </v-card>
                    <!-- <rich-resolution></rich-resolution> -->
                  </div>
                </v-tab-item>
                <v-tab-item key="main" class="tab">
                  <div class="pt-12 pb-12 pr-12 pl-12">
                    <case-resources-tab></case-resources-tab>
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
          <v-row no-gutters align="center" justify="end">
            <v-col cols="3" md="auto">
              <div class="last-updated-text grey--text">
                <v-icon small left v-if="selected.loading" class="loading-icon">mdi-loading</v-icon>
                <v-icon small left v-else>mdi-update</v-icon>
                <span class="subtitle-2 mr-4">{{ lastUpdatedTime }}</span>
              </div>
            </v-col>

            <v-spacer></v-spacer>

            <v-col cols="4" md="auto">
              <participant-chips
                :participants="selected.participants"
                :highlightedParticipants="[selected.assignee.individual.name]"
              ></participant-chips>
            </v-col>

            <v-col cols="5" md="auto" class="pr-2">
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

              <v-btn
                v-if="selected.status == 'New' || selected.status == 'Triage'"
                @click="showEscalateDialog(selected)"
                icon
              >
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
                </v-list>
              </v-menu>
            </v-col>
          </v-row>
          <v-card class="px-6 pb-6 mr-4 rounded-lg mt-8 refactoring-ui-shadow" outlined>
            <v-row no-gutters align="center" class="pt-6">
              <v-col cols="4">
                <div class="subtitle-2">Assigned to</div>
              </v-col>
              <v-col cols="8">
                <new-participant-select
                  :project="selected.project"
                  :value="selected.assignee"
                  @participant-change="onParticipantChange"
                />
              </v-col>
            </v-row>

            <v-row no-gutters align="center" class="pt-5">
              <v-col cols="4">
                <div class="subtitle-2">Reported by</div>
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
                <case-severity-select-chip :_case="selected" v-bind="attrs" v-on="on" />
              </v-col>
            </v-row>

            <!-- <v-row no-gutters align="center" class="pt-8">
              <v-col cols="4">
                <div class="subtitle-2">Type</div>
              </v-col>

              <v-col cols="8">
                <v-chip small text-color="black" color="#edf2f7">
                  {{ selected.case_type.name }}
                </v-chip>
              </v-col>
            </v-row>

            <v-row no-gutters align="center" class="pt-8">
              <v-col cols="4">
                <div class="subtitle-2">Project</div>
              </v-col>

              <v-col cols="8">
                <v-chip small text-color="black" color="#edf2f7">
                  {{ selected.project.name }}
                </v-chip>
              </v-col>
            </v-row> -->

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
                  <v-btn
                    small
                    class="lower-btn white--text"
                    color="info"
                    elevation="1"
                    @click="onSubmit()"
                  >
                    Submit
                  </v-btn>
                </v-col>
              </v-row>

              <!-- <v-row align="center" class="pt-8 pb-8 pr-4 pl-4">
                <v-divider></v-divider>
                <v-chip v-on="on" small color="grey lighten-2" @click="show = !show">
                  Additional Metadata
                  <v-icon small>{{ show ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
                </v-chip>
                <v-divider></v-divider>
              </v-row>
              <v-row no-gutters align="center">
                <v-col cols="2" md="9">
                  <v-chip small text-color="black" color="white" class="ml-4 mt-4">
                    <v-icon dense small class="pr-2"> mdi-content-duplicate </v-icon>
                    Duplicates
                    <v-icon small right>mdi-plus</v-icon>
                  </v-chip>
                  <v-chip small text-color="black" color="#edf2f7" class="ml-4 mt-4">
                    <v-icon dense small class="pr-2"> mdi-fire </v-icon>
                    Incidents
                    <v-icon small right>mdi-plus</v-icon>
                  </v-chip>
                  <v-badge small color="rgb(43, 51, 67)" content="2" class="mr-4"></v-badge>
                </v-col>

                <v-col cols="2" md="9" class="mb-2">
                  <v-chip small text-color="black" color="#edf2f7" class="ml-4 mt-4">
                    <v-icon dense small class="pr-2"> mdi-animation </v-icon>
                    Related
                    <v-icon small right>mdi-plus</v-icon>
                  </v-chip>
                  <v-badge small color="rgb(43, 51, 67)" content="0" class="mr-4"></v-badge>
                  <v-chip small text-color="black" color="#edf2f7" class="ml-4 mt-4">
                    <v-icon dense small class="pr-2"> mdi-tag </v-icon>
                    Tags
                    <v-icon small right>mdi-plus</v-icon>
                  </v-chip>
                  <v-badge small color="rgb(43, 51, 67)" content="17"></v-badge>
                </v-col>
              </v-row> -->
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
          </v-card>

          <v-row no-gutters align="center" class="pt-2">
            <v-col cols="24" md="9">
              <v-chip small text-color="black" color="#edf2f7" class="ml-2 mt-4 chip-hover-outline">
                <v-icon dense small class="pr-2"> mdi-content-duplicate </v-icon>
                Duplicates
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>

              <v-chip small text-color="black" color="#edf2f7" class="ml-4 mt-4 chip-hover-outline">
                <v-icon dense small class="pr-2"> mdi-fire </v-icon>
                Incidents
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>
              <v-badge color="rgb(43, 51, 67)" content="2" class="mr-4"></v-badge>

              <v-chip small text-color="black" color="#edf2f7" class="ml-2 mt-4 chip-hover-outline">
                <v-icon dense small class="pr-2"> mdi-animation </v-icon>
                Related
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>
              <v-badge small color="rgb(43, 51, 67)" content="0" class="mr-4"></v-badge>
              <v-chip small text-color="black" color="#edf2f7" class="ml-4 mt-4 chip-hover-outline">
                <v-icon dense small class="pr-2"> mdi-tag </v-icon>
                Tags
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>
              <v-badge small color="rgb(43, 51, 67)" content="17"></v-badge>
            </v-col>
          </v-row>

          <!-- <h4 class="mt-4 mb-2">Tags</h4>
          <tag-chips class="pb-16" :_case="selected"></tag-chips> -->
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

import CaseResourcesTab from "@/case/ResourcesTab.vue"
import CaseSeveritySelectChip from "@/case/severity/CaseSeveritySelectChip.vue"
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
    CaseSeveritySelectChip,
    CaseStatusSelectGroup,
    CaseTimelineAdvanced,
    CaseTimeline,
    CaseTimelineTab,
    CaseResourcesTab,
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
    const canvas = document.createElement("canvas")
    const context = canvas.getContext("2d")

    return {
      canvas,
      context,
      tab: null,
      show: false,
      editing: false,
      visibilityDialog: false,
      fullText: false,
      selectedLoading: false,
      clientlastUpdatedTime: null,
      currentReason: "Resolution Reason",
      visibilities: ["Open", "Restricted"],
      priorities: ["High", "Medium", "Low"],
      statuses: ["New", "Triage", "Escalated", "Closed"],
      resolutionReasons: ["False Positive", "User Acknowledged", "Mitigated", "Escalated"],
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

    lastUpdatedTime() {
      if (this.selected.updated_at) {
        if (this.clientlastUpdatedTime) {
          const timestamp = moment(this.clientlastUpdatedTime)
          return timestamp.fromNow()
        }
        const timestamp = moment(this.selected.updated_at)
        return timestamp.fromNow()
      } else {
        return "N/A"
      }
    },

    totalSignalInstances() {
      return this.selected.signal_instances.length
    },
  },

  methods: {
    updateClientUpdateTime() {
      this.clientlastUpdatedTime = new Date()
    },

    calculateTextWidth(text) {
      // Use the existing context to measure the text
      this.context.font = "300 2rem Roboto"
      return this.context.measureText(text).width
    },

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
      console.log(this.selected)
      this.save_page()
    },

    onSubmit(resolution_reason, resolution) {
      this.save_page()
    },

    autosave() {
      this.selectedLoading = true
      this.save_page()
      this.updateClientUpdateTime()
      this.selectedLoading = false
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

.chip-hover-outline:hover {
  border: 1px dashed rgba(148, 148, 148, 0.87) !important;
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

.last-updated-text {
  display: flex;
  align-items: center;
}

.loading-icon {
  animation: spin 1s infinite linear;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
