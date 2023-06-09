<template>
  <v-container fluid class="pt-6">
    <v-row no-gutters align="center">
      <v-col>
        <v-breadcrumbs :items="breadcrumbItems">
          <template v-slot:divider>
            <v-icon>mdi-chevron-right</v-icon>
          </template>
        </v-breadcrumbs>

        <!-- <div class="subtitle">
          <v-chip outlined color="red" class="mr-2">
            <v-icon dense class="pr-2" color="red lighten-2"> mdi-alert-plus-outline </v-icon>
            Critical </v-chip
          ><b>{{ _case.name }}</b> {{ _case.title }}
        </div> -->
        <div class="pl-6 pt-2 headline-5 font-weight-medium">{{ _case.title }}</div>
      </v-col>
      <v-col cols="auto">
        <v-btn outlined small color="secondary"
          ><v-icon small>mdi-chart-box-plus-outline</v-icon></v-btn
        >
      </v-col>
    </v-row>
    <v-divider class="mt-6 mb-6"></v-divider>
    <v-row>
      <v-col cols="9">
        <v-card>
          <v-tabs v-model="tab" background-color="grey lighten-4" hide-slider>
            <v-tab key="main" class="tab">
              <v-icon dense class="pr-2"> mdi-cube </v-icon>
            </v-tab>
            <v-tab key="entities" class="tab"> Entities </v-tab>
            <v-tab key="signals" class="tab">
              <v-icon dense small class="pr-2"> mdi-broadcast </v-icon> Signals
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="tab">
            <v-tab-item key="main">
              <!-- <entities-tab :selected="_case" v-model="signal_instances" /> -->
            </v-tab-item>
            <v-tab-item key="entities">
              <!-- <entities-tab :selected="_case" v-model="signal_instances" /> -->
            </v-tab-item>
            <v-tab-item key="signals">
              <signal-instance-card-viewer :caseId="_case.id" />
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
      <v-col cols="3">
        <v-card class="px-6 pt-6 pb-6">
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6">Assignee</div>
            </v-col>
            <v-col cols="auto">
              <new-participant :participant="_case.assignee" />
            </v-col>
          </v-row>
          <div class="pb-6">
            Reporter {{ _case.reporter ? _case.reporter.individual.name : "N/A" }}
          </div>
          <v-row no-gutters justify="space-between" align="center">
            <v-col cols="auto">
              <div class="pb-6">Status</div>
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
              <div class="pb-6">Priority</div>
            </v-col>
            <v-col cols="auto">
              <new-case-priority-select v-model="_case.case_priority" :project="_case.project" />
            </v-col>
          </v-row>
          <div>
            <v-textarea outlined name="input-7-4" label="Resolution" value=""></v-textarea>
          </div>
          <v-divider class="mt-6 mb-6"></v-divider>
          <div>
            <b>Timestamps</b>
          </div>
          <div>Created at {{ _case.created_at | formatRelativeDate }}</div>
          <div>Triaged at {{ _case.triage_at | formatRelativeDate }}</div>
          <div>Resolved at {{ _case.closed_at | formatRelativeDate }}</div>
          <div>Escalated at {{ _case.escalated_at | formatRelativeDate }}</div>
          <div>
            <b>Metrics</b>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import CaseTimelineTab from "@/case/TimelineTab.vue"
import NewParticipant from "@/case/NewParticipant.vue"
import NewCasePrioritySelect from "@/case/priority/NewCasePrioritySelect.vue"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"
import SignalInstanceCardViewer from "@/signal/SignalInstanceCardViewer.vue"
import EntitiesTab from "@/entity/EntitiesTab.vue"

export default {
  name: "CasePage",
  components: {
    CaseTimelineTab,
    NewParticipant,
    NewCasePrioritySelect,
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
  },

  created() {
    console.log("CasePage created", this._case)
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

.tab {
  transition: all 0.2s ease;
}
</style>
