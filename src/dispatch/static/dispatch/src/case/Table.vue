<template>
  <v-container fluid>
    <v-row class="align-center">
      <v-col cols="6">
        <div class="headline pl-4">Cases</div>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-row align="center" class="mt-2">
          <v-col cols="12" class="d-flex align-center justify-end">
            <!-- Expandable Search Bar -->
            <!-- <v-text-field
              v-model="table.options.q"
              prepend-inner-icon="mdi-card-search"
              class="pr-4"
              label="Search cases"
              hide-details
              clearable
              outlined
              rows="1"
              dense
              style="max-height: 200px"
            /> -->

            <!-- Filter Dialog -->
            <!-- <table-filter-dialog :projects="defaultUserProjects" /> -->

            <!-- Export Dialog -->
            <!-- <table-export-dialog /> -->

            <!-- New Button -->
            <!-- <v-btn
              color="grey darken-1"
              elevation="1"
              outlined
              small
              class="ml-2"
              @click="showNewSheet()"
              ><v-icon small class="ml-n1"> mdi-plus </v-icon>New case</v-btn
            > -->
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <!-- <v-divider class="mt-6"></v-divider>
    <v-col cols="6">
      <div class="subtitle pl-6">
        <v-badge bordered color="red" dot left offset-x="-10" offset-y="12">
          <b>Open cases</b>
        </v-badge>
      </div>
    </v-col> -->
    <div>
      <v-layout row wrap>
        <v-flex lg4 sm6 xs12 class="pb-6 pt-6">
          <case-stat-widget class="ml-6" icon="domain" title="129" sub-title="All Cases" />
        </v-flex>
        <v-flex lg4 sm6 xs12 class="pb-6 pt-6">
          <case-stat-widget class="ml-6" icon="domain" title="7" sub-title="Open Cases" />
        </v-flex>
        <v-flex lg4 sm6 xs12 class="pb-6 pt-6 pr-6">
          <case-stat-widget class="ml-6" icon="domain" title="1" sub-title="My Open Cases" />
        </v-flex>
      </v-layout>
    </div>
    <div>
      <new-case-chart></new-case-chart>
    </div>
    <div v-if="showEditSheet">
      <router-view />
    </div>
    <v-row no-gutters class="pt-0">
      <new-sheet />
      <workflow-run-modal />
      <escalate-dialog />
      <delete-dialog />
    </v-row>
    <v-row class="align-center pb-4">
      <v-col cols="6">
        <!-- Expandable Search Bar -->
      </v-col>
      <v-col cols="6" class="text-right">
        <v-row align="center" class="pt-2 pb-2">
          <v-col cols="12" class="d-flex align-center justify-end">
            <transition name="slide-fade">
              <v-text-field
                v-if="searchExpanded"
                v-model="table.options.q"
                color="black"
                prepend-inner-icon="mdi-magnify"
                class="pr-4"
                label="Search cases..."
                hide-details
                clearable
                solo
                outlined
                dense
              />
            </transition>
            <v-btn
              color="grey darken-3"
              elevation="1"
              outlined
              small
              class="ml-2"
              @click="searchExpanded = !searchExpanded"
            >
              <v-icon small class="ml-n1 mr-1"> mdi-magnify </v-icon>Search
            </v-btn>

            <!-- Filter Dialog -->
            <v-btn
              color="grey darken-3"
              elevation="1"
              outlined
              small
              class="ml-2"
              @click="showNewSheet()"
              ><v-icon small class="ml-n1 mr-1"> mdi-filter-variant </v-icon>Filter</v-btn
            >

            <!-- Export Dialog -->
            <v-btn
              color="grey darken-3"
              elevation="1"
              outlined
              small
              class="ml-2"
              @click="showNewSheet()"
              ><v-icon small class="ml-n1 mr-1"> mdi-export </v-icon>Export</v-btn
            >

            <!-- New Button -->
            <v-btn color="info" elevation="1" small class="ml-2" @click="showNewSheet()"
              ><v-icon small class="ml-n1 mr-1"> mdi-plus </v-icon>New</v-btn
            >
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card elevation="0">
          <v-data-table
            :headers="headers"
            :items="items"
            :server-items-length="total"
            :page.sync="page"
            :items-per-page.sync="itemsPerPage"
            :footer-props="{
              'items-per-page-options': [10, 25, 50, 100],
            }"
            :sort-by.sync="sortBy"
            :sort-desc.sync="descending"
            :loading="loading"
            v-model="selected"
            loading-text="Loading... Please wait"
            show-select
            @click:row="showCaseEditSheet"
          >
            <template v-slot:item.case_severity.name="{ item }">
              <case-severity :severity="item.case_severity.name" />
            </template>
            <template v-slot:item.case_priority.name="{ item }">
              <case-priority :priority="item.case_priority.name" />
            </template>
            <template v-slot:item.status="{ item }">
              <case-status :status="item.status" :id="item.id" />
            </template>
            <template v-slot:item.project.name="{ item }">
              <v-chip small :color="item.project.color" text-color="white">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template v-slot:item.assignee="{ item }">
              <case-participant :participant="item.assignee" />
            </template>
            <template v-slot:item.reported_at="{ item }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.reported_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.reported_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template v-slot:item.closed_at="{ item }">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on">{{ item.closed_at | formatRelativeDate }}</span>
                </template>
                <span>{{ item.closed_at | formatDate }}</span>
              </v-tooltip>
            </template>
            <template v-slot:item.data-table-actions="{ item }">
              <v-menu bottom left>
                <template v-slot:activator="{ on }">
                  <v-btn icon v-on="on">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item
                    :to="{
                      name: 'CaseTableEdit',
                      params: { name: item.name },
                    }"
                  >
                    <v-list-item-title>View / Edit</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    @click="showRun({ type: 'case', data: item })"
                    :disabled="item.status == 'Escalated' || item.status == 'Closed'"
                  >
                    <v-list-item-title>Run Workflow</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    @click="showEscalateDialog(item)"
                    :disabled="item.status == 'Escalated' || item.status == 'Closed'"
                  >
                    <v-list-item-title>Escalate</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="showDeleteDialog(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table>
          <!-- <v-divider class="mt-6"></v-divider> -->
          <v-col cols="6">
            <div class="subtitle pl-6">
              <v-badge bordered color="red" dot left offset-x="-10" offset-y="12">
                <b>My Open Cases</b>
              </v-badge>
            </div>
          </v-col>
          <case-card-iterator
            :items="openCases"
            :items-per-page="2"
            page.sync="page"
          ></case-card-iterator>
        </v-card>
      </v-col>
    </v-row>
    <bulk-edit-sheet />
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import BulkEditSheet from "@/case/BulkEditSheet.vue"
import CaseCard from "@/case/CaseCard.vue"
import CaseCardIterator from "@/case/CaseCardIterator.vue"
import CaseParticipant from "@/case/Participant.vue"
import CasePriority from "@/case/priority/CasePriority.vue"
import CaseSeverity from "@/case/severity/CaseSeverity.vue"
import CaseStatus from "@/case/CaseStatus.vue"
import NewCaseChart from "@/case/CaseChart.vue"
import DeleteDialog from "@/case/DeleteDialog.vue"
import EscalateDialog from "@/case/EscalateDialog.vue"
import CaseStatWidget from "@/case/CaseStatWidget.vue"
import NewSheet from "@/case/NewSheet.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"
import RouterUtils from "@/router/utils"
import TableExportDialog from "@/case/TableExportDialog.vue"
import TableFilterDialog from "@/case/TableFilterDialog.vue"

export default {
  name: "CaseTable",

  components: {
    CaseCard,
    CaseCardIterator,
    BulkEditSheet,
    CaseParticipant,
    CasePriority,
    CaseSeverity,
    CaseStatus,
    DeleteDialog,
    EscalateDialog,
    NewSheet,
    NewCaseChart,
    CaseStatWidget,
    WorkflowRunModal,
    TableExportDialog,
    TableFilterDialog,
  },

  props: {
    name: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      headers: [
        { text: "Name", value: "name", align: "left", width: "10%" },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status" },
        { text: "Type", value: "case_type.name", sortable: true },
        { text: "Severity", value: "case_severity.name", sortable: true },
        { text: "Priority", value: "case_priority.name", sortable: true },
        { text: "Project", value: "project.name", sortable: true },
        { text: "Assignee", value: "assignee", sortable: true },
        { text: "Reported At", value: "reported_at" },
        { text: "Closed At", value: "closed_at" },
        {
          text: "",
          value: "data-table-actions",
          sortable: false,
          align: "end",
        },
      ],
      showEditSheet: false,
      windowWidth: window.innerWidth,
      searchExpanded: false,
    }
  },

  computed: {
    ...mapFields("case_management", [
      "table.loading",
      "table.options.descending",
      "table.options.filters",
      "table.options.filters.assignee",
      "table.options.filters.case_priority",
      "table.options.filters.case_severity",
      "table.options.filters.case_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
      "table.rows.items",
      "table.rows.selected",
      "table.rows.total",
      "table",
    ]),
    ...mapFields("route", ["query"]),
    ...mapFields("auth", ["currentUser.projects"]),

    defaultUserProjects: {
      get() {
        let d = null
        if (this.projects) {
          let d = this.projects.filter((v) => v.default === true)
          return d.map((v) => v.project)
        }
        return d
      },
    },
    openCases() {
      return this.items.filter((item) => item.status !== "Closed")
    },
    firstThreeOpenCases() {
      // return the first three items from the openCases array
      return this.openCases.slice(0, 3)
    },
    visibleCases() {
      // Set the width of each card
      const cardWidth = 300
      // Compute the number of cards that will fit in the viewport
      const numberOfCards = Math.floor(this.windowWidth / cardWidth)

      console.log("numberOfCards", numberOfCards)

      // Return the slice of openCases that fits
      return this.openCases.slice(0, numberOfCards)
    },
  },

  methods: {
    ...mapActions("workflow", ["showRun"]),
    ...mapActions("case_management", [
      "getAll",
      "showNewSheet",
      "showDeleteDialog",
      "showEscalateDialog",
    ]),
    showCaseEditSheet(item) {
      this.$router.push({ name: "CaseTableEdit", params: { name: item.name } })
    },
    handleResize() {
      this.windowWidth = window.innerWidth
    },
  },

  watch: {
    $route: {
      immediate: true,
      handler: function (newVal) {
        this.showEditSheet = newVal.meta && newVal.meta.showEditSheet
      },
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.query),
      project: this.defaultUserProjects,
    }

    window.addEventListener("resize", this.handleResize)

    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [
        vm.case_priority,
        vm.case_severity,
        vm.case_type,
        vm.descending,
        vm.itemsPerPage,
        vm.project,
        vm.q,
        vm.reported_at.end,
        vm.reported_at.start,
        vm.sortBy,
        vm.status,
        vm.tag,
        vm.tag_type,
      ],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAll()
      }
    )
  },

  destroyed() {
    window.removeEventListener("resize", this.handleResize)
  },
}
</script>

<style scoped>
.align-center {
  align-items: center;
}

.v-btn {
  text-transform: none !important;
  /* color: rgb(39, 39, 39) !important; */
  font-weight: bold !important;
  letter-spacing: normal !important;
}

/* Add these styles for the transition animation */
.slide-fade-enter-active {
  transition: all 0.2s ease;
}
.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter,
.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
