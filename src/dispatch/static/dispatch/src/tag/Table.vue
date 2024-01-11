<template>
  <v-container fluid>
    <new-edit-sheet />
    <delete-dialog />
    <v-row align="center" justify="space-between" no-gutters>
      <v-col cols="8">
        <settings-breadcrumbs v-model="project" />
      </v-col>
      <v-col class="text-right">
        <v-btn color="info" class="mr-2" @click="createEditShow()"> New </v-btn>
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
            <template #item.discoverable="{ value }">
              <v-checkbox-btn :model-value="value" disabled />
            </template>
            <template #item.tag_type.name="{ item }">
              <span v-if="item.tag_type">
                {{ item.tag_type.name }}
              </span>
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

import DeleteDialog from "@/tag/DeleteDialog.vue"
import NewEditSheet from "@/tag/NewEditSheet.vue"
import SettingsBreadcrumbs from "@/components/SettingsBreadcrumbs.vue"

export default {
  name: "TagTable",

  components: {
    DeleteDialog,
    NewEditSheet,
    SettingsBreadcrumbs,
  },

  data() {
    return {
      headers: [
        { title: "Name", value: "name", sortable: true },
        { title: "Description", value: "description", sortable: false },
        { title: "Type", value: "tag_type.name", sortable: true },
        { title: "Source", value: "source", sortable: true },
        { title: "URI", value: "uri", sortable: false },
        { title: "External ID", value: "external_id", sortable: false },
        { title: "Discoverable", value: "discoverable", sortable: true },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("tag", [
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

  methods: {
    ...mapActions("tag", ["getAll", "createEditShow", "removeShow"]),
  },
}
</script>
