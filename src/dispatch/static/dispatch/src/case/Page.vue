<template>
  <v-container fluid class="pt-6" style="width: 1920px">
    <v-row no-gutters align="start">
      <v-col cols="9">
        <v-breadcrumbs :items="breadcrumbItems"> </v-breadcrumbs>

        <v-row align="center">
          <v-col cols="auto">
            <v-responsive :width="getTextWidth(selected.title) + 'px'">
              <!-- variant="flat" is currently undocumented-->
              <v-text-field
                variant="flat"
                background-color="transparent"
                class="hover-outline ml-2 mr-4"
                v-model="selected.title"
                hide-details="auto"
              >
              </v-text-field>
            </v-responsive>
          </v-col>

          <!-- <v-col cols="auto">
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
                  variant="flat"
                  auto-grow
                  rows="1"
                  hide-details="auto"
                  background-color="transparent"
                  @input="autosave"
                  class="pl-1 mb-4 mr-16 pr-16 hover-outline"
                >
                </v-textarea>
              </div>

              <div>
                <v-row no-gutters align="center">
                  <v-col cols="6" md="9">
                    <!-- <case-status-select-group :_case="selected"></case-status-select-group> -->
                  </v-col>
                </v-row>
              </div>

              <div class="pl-4">
                <v-tabs v-model="tab" class="ml-n3" background-color="transparent">
                  <v-tab key="main" c>
                    <v-icon dense small class="pr-2"> mdi-clock-outline </v-icon>
                    Timeline
                  </v-tab>
                  <v-tab key="resources">
                    <v-icon dense small class="pr-2"> mdi-semantic-web </v-icon>
                    Resources
                  </v-tab>
                  <v-tab key="signals" :disabled="signal_instances?.length === 0">
                    <v-icon dense small class="pr-2"> mdi-broadcast </v-icon>
                    <template v-if="totalSignalInstances">
                      <v-badge color="rgb(43, 51, 67)" inline :content="totalSignalInstances">
                        Signals
                      </v-badge>
                    </template>
                    <template v-else> Signals </template>
                  </v-tab>
                  <v-tab key="entities">
                    <v-icon dense small class="pr-2"> mdi-account-group </v-icon>
                    <template v-if="totalEntities > 0">
                      <v-badge color="rgb(43, 51, 67)" inline :content="totalEntities">
                        Entities
                      </v-badge>
                    </template>
                    <template v-else> Entities </template>
                  </v-tab>
                </v-tabs>
              </div>
              <v-divider class="ml-2"></v-divider>
              <v-window v-model="tab">
                <v-window-item key="main" class="tab">
                  <div class="pb-12 pr-12 pl-12">
                    <v-card elevation="0" class="rounded-lg">
                      <!-- <CaseTimeline class="pl-8 mr-4" /> -->
                    </v-card>
                  </div>
                </v-window-item>
                <v-window-item key="main" class="tab">
                  <div class="pb-12 pr-12 pl-12">
                    <case-resources-tab></case-resources-tab>
                  </div>
                </v-window-item>
                <v-window-item key="signals" class="tab">
                  <signal-instance-card-viewer :caseId="selected.id" />
                </v-window-item>
                <v-window-item key="entities">
                  <entities-tab :selected="selected" v-model="signal_instances" />
                </v-window-item>
              </v-window>
            </v-col>
          </v-row>
        </div>
      </v-col>
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
                v-if="selected.participants && selected.participants.length > 0"
                :participants="selected.participants"
              >
              </participant-chips>
            </v-col>
            <v-col cols="5" md="auto" class="pr-2">
              <v-btn class="ml-2" variant="text" icon @click="toggleVisibility()">
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
              <v-btn
                v-if="selected.status == 'New' || selected.status == 'Triage'"
                @click="showEscalateDialog(selected)"
                variant="text"
                icon
              >
                <v-icon dense>mdi-fire</v-icon>
              </v-btn>
              <v-menu offset-y>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn v-bind="attrs" v-on="on" variant="text" icon>
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
                <!-- <participant-select
                  v-model="selected.assignee"
                  :project="selected.project"
                  :value="selected.assignee"
                  @participant-change="onValueChange"
                /> -->
              </v-col>
            </v-row>
            <v-row no-gutters align="center" class="pt-5">
              <v-col cols="4">
                <div class="subtitle-2">Reported by</div>
              </v-col>
              <v-col cols="8">
                <!-- <participant-select
                  v-model="selected.reporter"
                  :project="selected.project"
                  :value="selected.reporter"
                  @participant-change="onValueChange"
                /> -->
              </v-col>
            </v-row>
            <v-row no-gutters align="center" class="pt-6">
              <v-col cols="4">
                <div class="subtitle-2">Priority</div>
              </v-col>
              <v-col cols="8">
                <!-- <case-priority-select-chip :_case="selected" v-bind="attrs" v-on="on" /> -->
              </v-col>
            </v-row>
            <v-row no-gutters align="center" class="pt-8">
              <v-col cols="4">
                <div class="subtitle-2">Severity</div>
              </v-col>
              <v-col cols="8">
                <!-- <case-severity-select-chip :_case="selected" v-bind="attrs" v-on="on" /> -->
              </v-col>
            </v-row>
            <v-row no-gutters align="center" class="pt-8">
              <v-col cols="4">
                <div class="subtitle-2">Type</div>
              </v-col>
              <v-col cols="8">
                <!-- <case-type-select-chip
                  v-model="selected.case_type"
                  :project="selected.project"
                  @input="onValueChange"
                /> -->
              </v-col>
            </v-row>
            <v-row no-gutters align="center" class="pt-8">
              <v-col cols="4">
                <div class="subtitle-2">Project</div>
              </v-col>
              <v-col cols="8">
                <project-select-chip v-model="selected.project" @input="onValueChange" />
              </v-col>
            </v-row>
            <v-divider class="mt-8"></v-divider>
            <div class="subtitle">Resolution Details</div>
            <v-card flat color="grey lighten-5" class="rounded-lg mt-8 hover-outline">
              <!-- <rich-editor></rich-editor> -->
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
            </v-card>
          </v-card>
          <v-dialog v-model="tagDialogVisable" max-width="800">
            <v-card>
              <v-btn disabled class="ml-4 mt-6" color="grey lighten-5" elevation="0">
                <v-icon color="grey darken-1"> mdi-tag </v-icon>
              </v-btn>
              <tag-filter-auto-complete
                label="Tags"
                v-model="tags"
                model="case"
                :model-id="id"
                class="pl-6 pr-6"
              />
              <v-btn class="mt-6 ml-6 mb-4" small color="info" elevation="1" @click="onSubmit">
                Submit
              </v-btn>
            </v-card>
          </v-dialog>
          <v-dialog v-model="dupeDialogVisable" max-width="800">
            <v-card>
              <v-card-title>Duplicates</v-card-title>
              <case-filter-combobox
                label="Duplicates"
                v-model="duplicates"
                :project="project"
                class="pl-6 pr-6"
              />
              <v-btn class="ml-6 mb-4" small color="info" elevation="1"> Submit </v-btn>
            </v-card>
          </v-dialog>
          <v-dialog v-model="relatedDialogVisable" max-width="800">
            <v-card>
              <v-card-title>Related</v-card-title>
              <case-filter-combobox
                label="Related"
                v-model="related"
                :project="project"
                class="pl-6 pr-6"
              />
              <v-btn class="ml-6 mb-4" small color="info" elevation="1"> Submit </v-btn>
            </v-card>
          </v-dialog>
          <v-dialog v-model="incidentDialogVisable" max-width="800">
            <v-card>
              <v-card-title>Incidents</v-card-title>
              <incident-filter-combobox
                label="Incidents"
                v-model="incidents"
                :project="project"
                class="pl-6 pr-6"
              />
              <v-btn class="ml-6 mb-4" small color="info" elevation="1"> Submit </v-btn>
            </v-card>
          </v-dialog>
          <v-row no-gutters align="center" class="pt-2">
            <v-col cols="24" md="9">
              <v-chip
                small
                text-color="black"
                color="#edf2f7"
                class="ml-2 mt-4 chip-hover-outline"
                @click="dupeDialogVisable = true"
              >
                <v-icon dense small class="pr-2"> mdi-content-duplicate </v-icon>
                Duplicates
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>
              <v-badge
                color="rgb(43, 51, 67)"
                :content="duplicates?.length ? duplicates?.length : '0'"
                class="mr-4"
              ></v-badge>
              <v-chip
                small
                text-color="black"
                color="#edf2f7"
                class="ml-4 mt-4 chip-hover-outline"
                @click="openIncidentDialog"
              >
                <v-icon dense small class="pr-2"> mdi-fire </v-icon>
                Incidents
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>
              <v-badge
                color="rgb(43, 51, 67)"
                :content="incidents?.length ? incidents?.length : '0'"
                class="mr-4"
              ></v-badge>
              <v-chip
                small
                text-color="black"
                color="#edf2f7"
                class="ml-2 mt-4 chip-hover-outline"
                @click="openRelatedDialog"
              >
                <v-icon dense small class="pr-2"> mdi-animation </v-icon>
                Related
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>
              <v-badge
                small
                color="rgb(43, 51, 67)"
                :content="related?.length ? related?.length : '0'"
                class="mr-4"
              ></v-badge>
              <v-chip
                small
                text-color="black"
                color="#edf2f7"
                class="ml-4 mt-4 chip-hover-outline"
                @click="openTagDialog"
              >
                <v-icon dense small class="pr-2"> mdi-tag </v-icon>
                Tags
                <v-icon small right>mdi-plus</v-icon>
              </v-chip>
              <v-badge
                small
                color="rgb(43, 51, 67)"
                :content="tags?.length ? tags?.length : '0'"
              ></v-badge>
            </v-col>
          </v-row>
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
import CaseFilterCombobox from "@/case/CaseFilterCombobox.vue"
import IncidentFilterCombobox from "@/incident/IncidentFilterCombobox.vue"
// import CaseTypeSelectChip from "@/case/type/CaseTypeSelectChip.vue"
// import CaseSeveritySelectChip from "@/case/severity/CaseSeveritySelectChip.vue"
// import CaseStatusSelectGroup from "@/case/CaseStatusSelectGroup.vue"
// import CasePrioritySelectChip from "@/case/priority/CasePrioritySelectChip.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"
import TagChips from "@/case/TagChips.vue"
import EscalateDialog from "@/case/EscalateDialog.vue"
import Participant from "@/case/Participant.vue"
import CasePrioritySelect from "@/case/priority/CasePrioritySelect.vue"
import ParticipantChips from "@/case/ParticipantChips.vue"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"
import SignalInstanceCardViewer from "@/signal/SignalInstanceCardViewer.vue"
// import RichEditor from "@/components/RichEditor.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import ProjectSelectChip from "@/project/ProjectSelectChip.vue"
export default {
  name: "CasePage",
  components: {
    EscalateDialog,
    // CaseSeveritySelectChip,
    // CaseTypeSelectChip,
    CaseFilterCombobox,
    // CaseStatusSelectGroup,
    IncidentFilterCombobox,
    CaseTimelineTab,
    CaseResourcesTab,
    // CasePrioritySelectChip,
    Participant,
    CasePrioritySelect,
    ParticipantChips,
    SignalInstanceTab,
    SignalInstanceCardViewer,
    EntitiesTab,
    TagFilterAutoComplete,
    TagChips,
    // RichEditor,
    ProjectSelectChip,
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
      tagDialogVisable: false,
      dupeDialogVisable: false,
      incidentDialogVisable: false,
      relatedDialogVisable: false,
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
    console.log("selected %O", this.selected)
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
      "selected.created_at",
      "selected.triage_at",
      "selected.closed_at",
      "selected.escalated_at",
      "selected.case_type",
      "selected.status",
      "selected.loading",
      "selected.incidents",
      "selected.related",
      "selected.duplicates",
      "selected.tags",
      "selected.signal_instances",
      "selected.workflow_instances",
      "dialogs.showEditSheet",
    ]),
    breadcrumbItems() {
      let items = [
        {
          title: "Cases",
          disabled: false,
          href: `/${this.$route.params.organization}/cases`,
        },
        {
          title: this.selected.name,
          disabled: true,
        },
      ]
      console.log("Items: ", items)
      return items
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
      return this.selected?.signal_instances?.length
    },
    totalEntities() {
      /*
        Walk through each signal instance and add the length of its entities
        array to a running sum, which is returned as the total number of entities.
        The 0 passed as the second argument to reduce is the initial value of the sum.
      */
      return this.selected?.signal_instances?.reduce((sum, instance) => {
        return sum + instance.entities?.length
      }, 0)
    },
  },
  methods: {
    updateClientUpdateTime() {
      this.clientlastUpdatedTime = new Date()
    },
    getTextWidth(text, font) {
      const canvas = document.createElement("canvas")
      const context = canvas.getContext("2d")
      context.font = "400 2rem Roboto"
      return context.measureText(text).width
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
    onValueChange() {
      console.log("this selected assignee %O", this.selected.assignee)
      this.save_page()
    },
    onTypeChange() {
      console.log("this selected type %O", this.selected.case_type)
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
      this.save_page()
      // other logic as necessary
    },
    ...mapActions("case_management", ["save", "getDetails", "save_page", "showEscalateDialog"]),
    toggleText() {
      this.fullText = !this.fullText
    },
    openRelatedDialog() {
      this.relatedDialogVisable = true
    },
    openDuplicateDialog() {
      this.dupeDialogVisable = true
    },
    openIncidentDialog() {
      this.incidentDialogVisable = true
    },
    openTagDialog() {
      this.tagDialogVisable = true
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
.v-tooltip__content {
  background-color: rgba(211, 211, 211, 0.8) !important;
  color: black !important;
  border: 1px dotted black !important;
}

.v-text-field input {
  font-size: 40px;
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
