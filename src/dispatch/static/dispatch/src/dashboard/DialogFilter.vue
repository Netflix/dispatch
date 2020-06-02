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
              :return-value.sync="dateRangeText"
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
              <v-date-picker v-model="window" type="month" range>
                <v-spacer></v-spacer>
                <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
                <v-btn text color="primary" @click="$refs.menu.save(date)">OK</v-btn>
              </v-date-picker>
            </v-menu>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-combobox v-model="filters.tag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="filters.incident_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="filters.incident_priority" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { map, sum, forEach, each, has } from "lodash"
// import IndividualCombobox from "@/individual/IndividualCombobox.vue"
import IncidentApi from "@/incident/api"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import subMonths from "date-fns/subMonths"
import { parseISO } from "date-fns"

export default {
  name: "IncidentOverviewFilterBar",

  methods: {
    fetchData() {
      let filterOptions = {}

      let localWindow = this.window
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
          if (has(value, "id")) {
            filterOptions.fields.push(key + ".id")
            filterOptions.values.push(value.id)
          } else {
            filterOptions.fields.push(key)
            filterOptions.values.push(value)
          }
          filterOptions.ops.push("==")
        })
      })

      IncidentApi.getAll(filterOptions).then(response => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
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
      window: [],
      filters: {
        tag: [],
        incident_type: [],
        incident_priority: []
      }
    }
  },

  created: function() {
    this.window = this.defaultDates
  },

  computed: {
    numFilters: function() {
      return sum([
        this.filters.incident_type.length,
        this.filters.incident_priority.length,
        this.filters.tag.length
      ])
    },
    queryDates() {
      // adjust for same month
      return map(this.dates, function(item) {
        return parseISO(item).toISOString()
      })
    },
    defaultDates() {
      return [this.defaultStart, this.defaultEnd]
    },
    today() {
      let now = new Date()
      return new Date(now.getFullYear(), now.getMonth(), now.getDate())
    },
    defaultStart() {
      return subMonths(this.today, 6)
        .toISOString()
        .substr(0, 10)
    },
    defaultEnd() {
      return this.today.toISOString().substr(0, 10)
    },
    dateRangeText() {
      return this.window.join(" ~ ")
    }
  },

  watch: {
    window: function() {
      this.fetchData()
    },
    filters: {
      deep: true,
      handler() {
        this.fetchData()
      }
    }
  }
}
</script>
