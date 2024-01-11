<template>
  <v-container fluid>
    <delete-dialog />
    <v-row no-gutters>
      <v-col>
        <div class="text-h5">Feedback</div>
      </v-col>
      <v-col class="text-right">
        <table-filter-dialog :projects="defaultUserProjects" />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col>
        <v-card variant="flat">
          <v-card-title>
            <v-text-field
              v-model="q"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
              clearable
            />
          </v-card-title>
          <v-data-table-server
            :headers="headers"
            :items="items"
            :items-length="total || 0"
            v-model:page="page"
            v-model:items-per-page="itemsPerPage"
            v-model:sort-by="sortBy"
            v-model:sort-desc="descending"
            :loading="loading"
            loading-text="Loading... Please wait"
          >
            <template #item.individual="{ item }">
              <participant
                v-if="item.individual"
                :participant="convertToParticipant(item.individual)"
              />
              <span v-else>(anonymous)</span>
            </template>
            <template #item.shift_end_at="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props" class="wavy-underline">{{
                    formatToUTC(item.shift_end_at)
                  }}</span>
                </template>
                <span class="pre-formatted">{{ formatToTimeZones(item.shift_end_at) }}</span>
              </v-tooltip>
            </template>
            <template #item.created_at="{ item }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(item.created_at) }}</span>
                </template>
                <span>{{ formatDate(item.created_at) }}</span>
              </v-tooltip>
            </template>
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.data-table-actions="{ item }">
              <v-menu location="right" origin="overlap">
                <template #activator="{ props }">
                  <v-btn icon variant="text" v-bind="props">
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item @click="removeShow(item)">
                    <v-list-item-title>Delete</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-data-table-server>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate, formatToUTC, formatToTimeZones } from "@/filters"

import DeleteDialog from "@/feedback/service/DeleteDialog.vue"
import Participant from "@/incident/Participant.vue"
import RouterUtils from "@/router/utils"
import TableFilterDialog from "@/feedback/service/TableFilterDialog.vue"

export default {
  name: "ServiceFeedbackTable",

  components: {
    DeleteDialog,
    Participant,
    TableFilterDialog,
  },

  data() {
    return {
      headers: [
        { title: "Shift End At (UTC)", value: "shift_end_at", sortable: true },
        { title: "Participant", value: "individual", sortable: true },
        { title: "Off-Shift Hours", value: "hours", sortable: true },
        { title: "Rating", value: "rating", sortable: true },
        { title: "Feedback", value: "feedback", sortable: true },
        { title: "Project", value: "project.name", sortable: false },
        { title: "Created At", value: "created_at", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate, formatDate, formatToUTC, formatToTimeZones }
  },

  computed: {
    ...mapFields("service_feedback", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.options.filters.project",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
    ]),
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
  },

  methods: {
    ...mapActions("service_feedback", ["getAll", "removeShow"]),
    convertToParticipant(individual) {
      return {
        individual: {
          name: individual.name,
          email: individual.email,
        },
      }
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...RouterUtils.deserializeFilters(this.$route.query),
      project: this.defaultUserProjects,
    }

    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending, vm.project],
      () => {
        this.page = 1
        RouterUtils.updateURLFilters(this.filters)
        this.getAll()
      }
    )
  },
}
</script>

<style scoped lang="css">
.pre-formatted {
  white-space: pre;
}
</style>
