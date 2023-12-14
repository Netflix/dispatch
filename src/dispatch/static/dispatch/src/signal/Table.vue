<template>
  <v-container fluid>
    <new-edit-dialog />
    <delete-dialog />
    <v-row no-gutters>
      <v-col>
        <v-alert closable icon="mdi-school" prominent text type="info">
          Signal definitions determine how a signal is processed. Allowing you to map case types,
          snooze and duplication rules for each signal.
        </v-alert>
      </v-col>
    </v-row>
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <v-col class="text-right">
        <v-btn color="info" class="ml-2" @click="createEditShow()"> New </v-btn>
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
            <template #item.create_case="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.enabled="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.status="{ item, value }">
              <case-status :status="value" :id="item.id" />
            </template>
            <template #item.project.name="{ item }">
              <v-chip size="small" :color="item.project.color">
                {{ item.project.name }}
              </v-chip>
            </template>
            <template #item.case_type="{ item }">
              <v-chip v-if="item.case_type" size="small" color="info">
                {{ item.case_type.name }}
              </v-chip>
            </template>
            <template #item.case_priority="{ item }">
              <v-chip v-if="item.case_priority" size="small" :color="item.case_priority.color">
                {{ item.case_priority.name }}
              </v-chip>
            </template>
            <template #item.external_url="{ item }">
              <v-btn
                v-if="item.external_url"
                :href="item.external_url"
                target="_blank"
                icon
                variant="text"
              >
                <v-icon>mdi-open-in-new</v-icon>
              </v-btn>
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
import NewEditDialog from "@/signal/NewEditDialog.vue"
import DeleteDialog from "@/signal/DeleteDialog.vue"

export default {
  name: "SignalTable",
  components: { NewEditDialog, DeleteDialog },
  props: {
    name: {
      type: String,
      default: null,
    },
  },
  data() {
    return {
      headers: [
        { title: "Name", value: "name", align: "left", width: "10%" },
        { title: "Variant", value: "variant", sortable: true },
        { title: "Description", value: "description", sortable: false },
        { title: "Create Case", value: "create_case", sortable: true, width: "100px" },
        { title: "Enabled", value: "enabled", sortable: true },
        { title: "Owner", value: "owner" },
        { title: "Case Type", value: "case_type" },
        { title: "Case Priority", value: "case_priority" },
        { title: "External URL", value: "external_url", sortable: false },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
      showEditSheet: false,
    }
  },
  computed: {
    ...mapFields("signal", [
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
    ...mapFields("auth", ["currentUser.projects"]),
  },
  methods: {
    ...mapActions("signal", ["getAll", "createEditShow", "removeShow"]),
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
