<template>
  <v-menu offset-y>
    <template v-slot:activator="{ on, attrs }">
      <v-chip v-bind="attrs" v-on="on" small class="mr-2 hover-outline" color="#edf2f7">
        {{ project ? project.name : "None" }}
      </v-chip>
    </template>
    <v-list>
      <v-list-item v-for="(item, index) in items" :key="index" @click="changeProject(item)">
        {{ item.name }}
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { cloneDeep, debounce } from "lodash"
import ProjectApi from "@/project/api"
export default {
  name: "ProjectSelectChip",
  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: "Project",
    },
  },
  data() {
    return {
      loading: false,
      items: [],
      numItems: 5,
      more: false,
      search: null,
    }
  },
  computed: {
    project: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },
  methods: {
    // Other methods
    changeProject(project) {
      this.value = project // Update the selected case type.
      this.$emit("input", project) // Emit the new value
    },
    updateProject(project) {
      // Call an API to update the project on the backend.
      // Adjust this method to suit your API structure.
      ProjectApi.update(project.id, project)
        .then((response) => {
          // Handle the response as needed
        })
        .catch((error) => {
          // Handle the error as needed
        })
    },
    fetchData() {
      this.error = null
      this.loading = true
      // Remove the itemsPerPage from the filterOptions to fetch all items
      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        descending: [false],
      }
      ProjectApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        if (this.project) {
          // Check to see if the current selection is available in the list, if not, we add it
          if (!this.items.find((match) => match.id === this.project.id)) {
            this.items = [this.project].concat(this.items)
          }
        }
        this.loading = false
      })
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
  created() {
    this.fetchData()
  },
}
</script>

<style scoped>
.hover-outline:hover {
  border: 1px dashed rgba(148, 148, 148, 0.87) !important;
  border-radius: 20px;
}
</style>
