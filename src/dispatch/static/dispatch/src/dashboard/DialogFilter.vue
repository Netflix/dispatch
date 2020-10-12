<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap :content="numFilters">
        <v-btn color="secondary" dark v-on="on">Filter</v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <v-menu
              ref="menu"
              v-model="menu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field
                  v-model="dateRangeText"
                  label="Window"
                  readonly
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker v-model="localWindow" type="month" range> </v-date-picker>
            </v-menu>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-combobox v-model="localTag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="localIncidentType" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="localIncidentPriority" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { map, sum, forEach, each, has, assign } from "lodash"
// import IndividualCombobox from "@/individual/IndividualCombobox.vue"
import IncidentApi from "@/incident/api"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import subMonths from "date-fns/subMonths"
import { parseISO } from "date-fns"

export default {
  name: "IncidentOverviewFilterBar",

  props: {
    tag: {
      type: [String, Array],
      default: function() {
        return []
      }
    },
    incident_type: {
      type: [String, Array],
      default: function() {
        return []
      }
    },
    incident_priority: {
      type: [String, Array],
      default: function() {
        return []
      }
    },
    window: {
      type: Array,
      default: function() {
        let now = new Date()
        let today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        let start = subMonths(today, 6)
          .toISOString()
          .substr(0, 10)
        let end = today.toISOString().substr(0, 10)
        return [start, end]
      }
    }
  },

  methods: {
    fetchData() {
      let filterOptions = {}

      let localWindow = this.localWindow
      // ensure we have a decent date string
      localWindow = map(localWindow, function(item) {
        return parseISO(item).toISOString()
      })

      if (localWindow.length == 1) {
        localWindow[1] = localWindow[0]
      }

      // we always window
      filterOptions.itemsPerPage = -1
      filterOptions.sortBy = ["reported_at"]
      filterOptions.descending = [false]
      filterOptions.fields = ["reported_at", "reported_at"]
      filterOptions.ops = [">=", "<="]
      filterOptions.values = localWindow

      forEach(this.filters, function(value, key) {
        each(value, function(value) {
          if (typeof value === "string") {
            filterOptions.fields.push(key + ".name")
            filterOptions.values.push(value)
          } else if (has(value, "id")) {
            filterOptions.fields.push(key + ".id")
            filterOptions.values.push(value.id)
          } else {
            filterOptions.fields.push(key)
            filterOptions.values.push(value)
          }
          filterOptions.ops.push("==")
        })
      })

      this.$emit("loading", true)
      IncidentApi.getAll(filterOptions).then(response => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
    serializeFilters() {
      let flatFilters = {}
      forEach(this.filters, function(value, key) {
        each(value, function(item) {
          if (has(flatFilters, key)) {
            flatFilters[key].push(item.name)
          } else {
            flatFilters[key] = [item.name]
          }
        })
      })
      return flatFilters
    },
    serializeWindow() {
      return { start: this.localWindow[0], end: this.localWindow[1] }
    },
    updateURL() {
      let queryParams = {}
      assign(queryParams, this.serializeFilters())
      assign(queryParams, this.serializeWindow())
      this.$router.replace({ query: queryParams })
    }
  },

  components: {
    // IndividualCombobox,
    TagFilterCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox
  },

  data() {
    return {
      menu: false,
      display: false,
      localWindow: this.window,
      localTag: typeof this.tag === "string" ? [this.tag] : this.tag,
      localIncidentPriority:
        typeof this.incident_priority === "string"
          ? [this.incident_priority]
          : this.incident_priority,
      localIncidentType:
        typeof this.incident_type === "string" ? [this.incident_type] : this.incident_type
    }
  },

  mounted() {
    this.$watch(
      vm => [vm.localWindow, vm.localTag, vm.localIncidentPriority, vm.localIncidentType],
      () => {
        this.updateURL()
        this.fetchData()
      }
    )
  },

  created() {
    this.fetchData()
  },

  computed: {
    filters() {
      return {
        tag: this.localTag,
        incident_priority: this.localIncidentPriority,
        incident_type: this.localIncidentType
      }
    },
    numFilters: function() {
      return sum([
        this.localIncidentType.length,
        this.localIncidentPriority.length,
        this.localTag.length,
        1
      ])
    },
    dateRangeText() {
      return this.localWindow.join(" ~ ")
    }
  }
}
</script>
