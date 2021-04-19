<template>
  <v-layout wrap>
    <new-edit-sheet />
    <div class="headline">Plugins</div>
    <v-spacer />
    <v-btn color="info" class="ml-2" @click="createEditShow()"> New </v-btn>
    <v-flex xs12>
      <v-layout column>
        <v-flex>
          <v-card elevation="0">
            <v-card-title>
              <v-text-field
                v-model="q"
                append-icon="search"
                label="Search"
                single-line
                hide-details
                clearable
              />
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="items"
              :server-items-length="total"
              :page.sync="page"
              :items-per-page.sync="itemsPerPage"
              :sort-by.sync="sortBy"
              :sort-desc.sync="descending"
              :loading="loading"
              loading-text="Loading... Please wait"
            >
              <template v-slot:item.author="{ item }">
                <a :href="item.author_url" target="_blank" style="text-decoration: none">
                  {{ item.author }}
                  <v-icon small>open_in_new</v-icon>
                </a>
              </template>
              <template v-slot:item.enabled="{ item }">
                <v-simple-checkbox v-model="item.enabled" disabled />
              </template>
              <template v-slot:item.plugin.multiple="{ item }">
                <v-simple-checkbox v-model="item.plugin.multiple" disabled />
              </template>
              <template v-slot:item.plugin.required="{ item }">
                <v-simple-checkbox v-model="item.plugin.required" disabled />
              </template>
              <template v-slot:item.data-table-actions="{ item }">
                <v-menu bottom left>
                  <template v-slot:activator="{ on }">
                    <v-btn icon v-on="on">
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item @click="createEditShow(item)">
                      <v-list-item-title>View / Edit</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </template>
            </v-data-table>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import NewEditSheet from "@/plugin/NewEditSheet.vue"
export default {
  name: "PluginTable",

  components: {
    NewEditSheet,
  },
  data() {
    return {
      headers: [
        { text: "Title", value: "plugin.title", sortable: true },
        { text: "Slug", value: "plugin.slug", sortable: true },
        { text: "Author", value: "plugin.author", sortable: true },
        { text: "Version", value: "plugin.version", sortable: true },
        { text: "Enabled", value: "enabled", sortable: true },
        { text: "Required", value: "plugin.required", sortable: true },
        { text: "Multiple Allowed", value: "plugin.multiple", sortable: true },
        { text: "Type", value: "plugin.type", sortable: true },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },

  computed: {
    ...mapFields("plugin", [
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
    ...mapFields("route", ["query"]),
  },

  created() {
    this.project = [{ name: this.query.project }]

    this.getAllInstances()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAllInstances()
      }
    )

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending],
      () => {
        this.page = 1
        this.getAllInstances()
      }
    )
  },

  methods: {
    ...mapActions("plugin", ["getAllInstances", "createEditShow"]),
  },
}
</script>
