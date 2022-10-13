<template>
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
    <template v-slot:item.name="{ item }">
      <router-link :to="{ name: 'ProjectSettings', query: { project: item.name } }">
        {{ item.name }}
      </router-link>
    </template>
    <template v-slot:item.default="{ item }">
      <v-btn icon v-on="on" @click="markDefault(item)">
        <v-icon v-if="item.default">mdi-star</v-icon>
        <v-icon v-else="item.default">mdi-star-outline</v-icon>
      </v-btn>
    </template>
    <template v-slot:item.role="{ item }">
      <v-select :items="projectRoles"> </v-select>
    </template>
  </v-data-table>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "OrganizationMemberProjectTable",

  components: {},

  data() {
    return {
      projectRoles: ["Member", "Admin", "Owner"],
      headers: [
        { text: "Default", value: "default", sortable: false },
        { text: "Name", value: "name", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Role", value: "role", sortable: false },
      ],
    }
  },

  computed: {
    ...mapFields("project", [
      "table.options.q",
      "table.options.page",
      "table.options.itemsPerPage",
      "table.options.sortBy",
      "table.options.descending",
      "table.loading",
      "table.rows.items",
      "table.rows.total",
    ]),
  },

  created() {
    this.getAll()

    this.$watch(
      (vm) => [vm.page],
      () => {
        this.getAll()
      }
    )

    this.$watch(
      (vm) => [vm.q, vm.itemsPerPage, vm.sortBy, vm.descending],
      () => {
        this.page = 1
        this.getAll()
      }
    )
  },

  methods: {
    ...mapActions("project", ["getAll"]),
  },
}
</script>
