<template>
  <v-menu offset-y>
    <template v-slot:activator="{ on, attrs }">
      <v-chip v-bind="attrs" v-on="on" small class="mr-2 hover-outline" color="#edf2f7">
        {{ value ? value.name : "None" }}
      </v-chip>
    </template>
    <v-list>
      <v-list-item v-for="(item, index) in items" :key="index" @click="changeCaseType(item)">
        {{ item.name }}
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { cloneDeep, debounce } from "lodash"
import { mapActions } from "vuex"

import SearchUtils from "@/search/utils"
import CaseTypeApi from "@/case/type/api"

export default {
  name: "CaseTypeSelectChip",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    project: {
      type: [Object],
      default: null,
    },
    hint: {
      type: String,
      default: function () {
        return "Case Type to associate"
      },
    },
    label: {
      type: String,
      default: function () {
        return "Case Type"
      },
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
    case_type: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  methods: {
    ...mapActions("case_management", ["save_page"]),

    changeCaseType(type) {
      this.value = type // Update the selected case type.
      this.$emit("input", type) // Emit the new value
    },

    fetchData() {
      this.error = null
      this.loading = true

      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        descending: [false],
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
            enabled: ["true"],
          },
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      CaseTypeApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items

        if (this.case_type) {
          // check to see if the current selection is available in the list and if not we add it
          if (!this.items.find((match) => match.id === this.case_type.id)) {
            this.items = [this.case_type].concat(this.items)
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
