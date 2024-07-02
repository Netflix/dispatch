<template>
  <v-container fluid>
    <div v-if="showEditSheet">
      <router-view />
    </div>
    <v-row no-gutters>
      <new-sheet />
      <workflow-run-modal />
      <escalate-dialog />
      <delete-dialog />
      <v-col>
        <div class="text-h5">Cases</div>
      </v-col>
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
        <table-export-dialog />
        <v-btn
          nav
          variant="flat"
          color="error"
          :to="{ name: 'caseReport' }"
          class="ml-2"
          hide-details
        >
          <v-icon start color="white">mdi-shield-search</v-icon>
          <span class="text-uppercase text-body-2 font-weight-bold">Report case</span>
        </v-btn>
        <v-btn
          v-if="userAdminOrAbove(currentUserRole)"
          color="info"
          class="ml-2"
          @click="showNewSheet()"
        >
          New
        </v-btn>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card variant="flat">
          <v-card-title>
            <v-text-field
              v-model="q"
              append-inner-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
              clearable
            />
          </v-card-title>
          <v-data-table-server
            show-select
            return-object
            :headers="headers"
            :items="items"
            :items-length="total || 0"
            :loading="loading"
            v-model="selected"
            loading-text="Loading... Please wait"
            :sort-by="['reported_at']"
            :items-per-page="itemsPerPage"
            @click:row="showCasePage"
            @update:options="loadItems"
            :footer-props="{
              'items-per-page-options': [10, 25, 50, 100],
            }"
          >
            <template #item.case_severity.name="{ value }">
              <case-severity :severity="value" />
            </template>
            <template #item.case_priority.name="{ value }">
              <case-priority :priority="value" />
            </template>
            <template #item.status="{ item }">
              <case-status
                :status="item.status"
                :id="item.id"
                :allowSelfJoin="item.project.allow_self_join"
                :dedicatedChannel="item.dedicated_channel"
              />
            </template>
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.assignee="{ value }">
              <case-participant :participant="value" />
            </template>
            <template #item.reported_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.closed_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.data-table-actions="{ item }">
              <v-menu location="right" origin="overlap">
                <template #activator="{ props }">
                  <v-btn icon variant="text" v-bind="props">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item
                    :to="{
                      name: 'CasePage',
                      params: { name: item.name },
                    }"
                  >
                    <v-list-item-title>View</v-list-item-title>
                  </v-list-item>
                  <v-list-item
                    :to="{
                      name: 'CaseTableEdit',
                      params: { name: item.name },
                    }"
                  >
                    <v-list-item-title>Edit</v-list-item-title>
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
          </v-data-table-server>
        </v-card>
      </v-col>
    </v-row>
    <bulk-edit-sheet />
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { useStore } from "vuex"
import { useRoute, useRouter } from "vue-router"
import { formatRelativeDate, formatDate } from "@/filters"

import BulkEditSheet from "@/case/BulkEditSheet.vue"
import CaseParticipant from "@/case/Participant.vue"
import CasePriority from "@/case/priority/CasePriority.vue"
import CaseSeverity from "@/case/severity/CaseSeverity.vue"
import CaseStatus from "@/case/CaseStatus.vue"
import DeleteDialog from "@/case/DeleteDialog.vue"
import EscalateDialog from "@/case/EscalateDialog.vue"
import NewSheet from "@/case/NewSheet.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"
import RouterUtils from "@/router/utils"
import TableExportDialog from "@/case/TableExportDialog.vue"
import TableFilterDialog from "@/case/TableFilterDialog.vue"

const store = useStore()
const router = useRouter()
const route = useRoute()

const itemsPerPage = ref(25)
const showEditSheet = ref(false)

const headers = [
  { title: "Name", value: "name", align: "left", width: "10%" },
  { title: "Title", value: "title", sortable: false },
  { title: "Status", value: "status" },
  { title: "Type", value: "case_type.name", sortable: true },
  { title: "Severity", value: "case_severity.name", sortable: true },
  { title: "Priority", value: "case_priority.name", sortable: true },
  { title: "Project", value: "project.name", sortable: true },
  { title: "Assignee", value: "assignee", sortable: false },
  { title: "Reported At", value: "reported_at", sortable: true },
  { title: "Closed At", value: "closed_at", sortable: true },
  { title: "", key: "data-table-actions", sortable: false, align: "end" },
]

const caseManagement = computed(() => store.state.case_management)
const auth = computed(() => store.state.auth)

const defaultUserProjects = computed(() => {
  let d = null

  if (auth.value.currentUser.projects) {
    let d = auth.value.currentUser.projects.filter((v) => v.default === true)
    return d.map((v) => v.project)
  }
  return d
})

const showRun = (data) => store.dispatch("workflow/showRun", data)
const showEscalateDialog = (item) => store.dispatch("case_management/showEscalateDialog", item)
const showDeleteDialog = (item) => store.dispatch("case_management/showDeleteDialog", item)
const showNewSheet = () => store.dispatch("case_management/showNewSheet")

const getAll = () => {
  store.dispatch("case_management/getAll", caseManagement.value.table.options)
}

const items = computed(() => caseManagement.value.table.rows.items)
const total = computed(() => caseManagement.value.table.rows.total)
const loading = computed(() => caseManagement.value.table.loading)
const currentUserRole = computed(() => caseManagement.value.current_user_role)

const selected = ref([])
watch(selected, (newVal) => {
  caseManagement.value.table.rows.selected = newVal
})

const showCasePage = (e, { item }) => {
  router.push({ name: "CasePage", params: { name: item.name } })
}

function loadItems({ page, itemsPerPage, sortBy }) {
  caseManagement.value.table.options.page = page
  caseManagement.value.table.options.itemsPerPage = itemsPerPage
  // Check if sortBy is an array of objects (after manual click)
  if (sortBy.length && typeof sortBy[0] === "object") {
    // Take the first sort option
    const sortOption = sortBy[0]

    caseManagement.value.table.options.sortBy = [sortOption.key]
    caseManagement.value.table.options.descending = [sortOption.order === "desc"]
  } else {
    caseManagement.value.table.options.sortBy = sortBy
  }
  getAll()
}

function userAdminOrAbove(role) {
  return ["Admin", "Owner", "Manager"].includes(role)
}

watch(
  route,
  (newVal) => {
    showEditSheet.value = newVal.meta && newVal.meta.showEditSheet
  },
  { immediate: true }
)

const q = ref(caseManagement.value.table.options.q)
watch(
  () => q.value,
  (newValue) => {
    caseManagement.value.table.options.q = newValue
    getAll()
  }
)

// Deserialize the URL filters and apply them to the local filters
const filters = {
  ...RouterUtils.deserializeFilters(route.query),
  project: defaultUserProjects,
}
store.commit("case_management/SET_FILTERS", filters)
watch(
  () => caseManagement.value.table.options.filters,
  (newFilters, oldFilters) => {
    // Check if the filters have changed
    if (JSON.stringify(newFilters) !== JSON.stringify(oldFilters)) {
      // Update the URL filters
      RouterUtils.updateURLFilters(newFilters)

      // Fetch all items with the updated filters
      getAll()
    }
  },
  { deep: true } // Required to watch object properties inside filters
)
</script>
