<template>
  <v-container fluid>
    <search-filter-create-dialog />
    <edit-dialog />
    <delete-dialog />
    <v-row no-gutters>
      <v-col>
        <v-alert closable icon="mdi-school" prominent text type="info">
          Search filters enable you to define under which conditions an individual, oncall service,
          or team need to be engaged in an incident, or when a notification needs to be sent.
        </v-alert>
      </v-col>
    </v-row>
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <v-col class="text-right">
        <v-btn color="info" class="mr-2" @click="showCreateDialog()"> New </v-btn>
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
            <!-- TODO(mvilanova): Allow to view the list of individuals, teams, services, and notifications upon clicking on the chip -->
            <template #item.individuals="{ item }">
              <v-chip v-if="item.individuals.length == 0" size="small" color="green">
                {{ item.individuals.length }}
              </v-chip>
              <v-chip v-if="item.individuals.length > 0" size="small" color="red">
                {{ item.individuals.length }}
              </v-chip>
            </template>
            <template #item.teams="{ item }">
              <v-chip v-if="item.teams.length == 0" size="small" color="green">
                {{ item.teams.length }}
              </v-chip>
              <v-chip v-if="item.teams.length > 0" size="small" color="red">
                {{ item.teams.length }}
              </v-chip>
            </template>
            <template #item.services="{ item }">
              <v-chip v-if="item.services.length == 0" size="small" color="green">
                {{ item.services.length }}
              </v-chip>
              <v-chip v-if="item.services.length > 0" size="small" color="red">
                {{ item.services.length }}
              </v-chip>
            </template>
            <template #item.notifications="{ item }">
              <v-chip v-if="item.notifications.length == 0" size="small" color="green">
                {{ item.notifications.length }}
              </v-chip>
              <v-chip v-if="item.notifications.length > 0" size="small" color="red">
                {{ item.notifications.length }}
              </v-chip>
            </template>
            <template #item.enabled="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.created_at="{ value }">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ formatRelativeDate(value) }}</span>
                </template>
                <span>{{ formatDate(value) }}</span>
              </v-tooltip>
            </template>
            <template #item.updated_at="{ value }">
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
                  <v-list-item @click="createEditShow(item)">
                    <v-list-item-title>View / Edit</v-list-item-title>
                  </v-list-item>
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
import { formatRelativeDate, formatDate } from "@/filters"

import DeleteDialog from "@/search/DeleteDialog.vue"
import SearchFilterCreateDialog from "@/search/SearchFilterCreateDialog.vue"
import EditDialog from "@/search/EditDialog.vue"

export default {
  name: "SearchFilterTable",

  components: { DeleteDialog, SearchFilterCreateDialog, EditDialog },

  data() {
    return {
      headers: [
        { title: "Name", value: "name", align: "left", width: "10%" },
        { title: "Description", value: "description", sortable: false },
        { title: "Individuals", value: "individuals" },
        { title: "Teams", value: "teams" },
        { title: "Services", value: "services" },
        { title: "Notifications", value: "notifications" },
        { title: "Creator", value: "creator.email" },
        { title: "Created At", value: "created_at" },
        { title: "Updated At", value: "updated_at" },
        { title: "Enabled", value: "enabled" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },

  setup() {
    return { formatRelativeDate, formatDate }
  },

  computed: {
    ...mapFields("search", [
      "table.loading",
      "table.options.descending",
      "table.options.filters.project",
      "table.options.itemsPerPage",
      "table.options.page",
      "table.options.q",
      "table.options.sortBy",
      "table.rows.items",
      "table.rows.total",
    ]),
  },

  methods: {
    ...mapActions("search", ["getAll", "createEditShow", "showCreateDialog", "removeShow"]),
  },

  created() {
    this.project = [{ name: this.$route.query.project }]
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
        this.$router.push({ query: { project: this.project[0].name } })
        this.getAll()
      }
    )
  },
}
</script>

<style>
.mdi-school {
  color: white !important;
}
</style>
