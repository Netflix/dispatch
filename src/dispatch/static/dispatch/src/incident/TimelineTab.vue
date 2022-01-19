<template>
  <v-container>
    <v-row justify="end">
      <v-switch v-model="showDetails" label="Show details" />
      <v-btn
        color="secondary"
        class="ml-2 mr-2 mt-3"
        @click="exportToCSV()"
        :loading="exportLoading"
      >
        Export
      </v-btn>
    </v-row>
    <v-timeline v-if="events && events.length" dense clipped>
      <v-timeline-item
        v-for="event in sortedEvents"
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
  name: "IncidentTimelineTab",

  data() {
    return {
      showDetails: false,
      exportLoading: false,
    }
  },

  computed: {
    ...mapFields("incident", ["selected.events", "selected.name"]),

    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
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
