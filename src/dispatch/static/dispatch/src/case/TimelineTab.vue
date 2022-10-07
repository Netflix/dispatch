<style scoped>
.v-input--selection-controls {
  padding-top: 15px;
}
</style>
<template>
  <v-container>
    <v-toolbar style="border-bottom: 1px solid #dddddd" flat dense>
      <v-text-field
        v-model="searchTerm"
        prepend-icon="search"
        label="Filter"
        single-line
        hide-details
        solo
        flat
        class="pb-1"
      />
      <v-spacer />
      <v-switch dense v-model="showDetails" inset />
      <v-btn icon @click="exportToCSV()" :loading="exportLoading">
        <v-icon>mdi-table-arrow-right</v-icon>
      </v-btn>
    </v-toolbar>
    <v-timeline v-if="events && events.length" dense clipped>
      <v-timeline-item
        v-for="event in filteredEvents"
        :key="event.id"
        class="mb-4"
        color="blue"
        small
      >
        <v-row justify="space-between">
          <v-col cols="7">
            {{ event.description }}
            <transition-group name="slide" v-if="showDetails">
              <template v-for="(value, key) in event.details">
                <v-card flat :key="key">
                  <v-card-title class="subtitle-1">
                    {{ key | snakeToCamel }}
                  </v-card-title>
                  <v-card-text>{{ value }}</v-card-text>
                </v-card>
              </template>
            </transition-group>
            <div class="caption">
              {{ event.source }}
            </div>
          </v-col>
          <v-col class="text-right" cols="5">
            {{ event.started_at | formatRelativeDate }}
          </v-col>
        </v-row>
      </v-timeline-item>
    </v-timeline>
    <div v-else>
      <p class="text-center">No timeline data available.</p>
    </div>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import Util from "@/util"

export default {
  name: "CaseTimelineTab",

  data() {
    return {
      showDetails: false,
      exportLoading: false,
      searchTerm: "",
    }
  },

  computed: {
    ...mapFields("case_management", ["selected.events", "selected.name"]),

    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
    filteredEvents() {
      if (this.searchTerm.length) {
        return this.events.filter((event) => {
          return !event.description.toLowerCase().includes(this.searchTerm.toLowerCase())
        })
      } else {
        return this.events
      }
    },
  },

  methods: {
    exportToCSV() {
      this.exportLoading = true
      let items = this.sortedEvents
      Util.exportCSV(items, this.name + "-timeline-export.csv")
      this.exportLoading = false
    },
  },
}
</script>
