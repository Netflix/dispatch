<template>
  <v-container>
    <v-row justify="end" class="align-items-baseline">
      <v-switch v-model="showDetails" label="Show details" />
      <v-btn
        color="secondary"
        class="ml-2 mr-2 mt-3"
        @click="exportToCSV()"
        :loading="exportLoading"
      >
        Export
      </v-btn>
      <timeline-filter-dialog ref="filter_dialog" />
      <edit-event-dialog />
      <delete-event-dialog />
    </v-row>
    <v-timeline v-if="events && events.length" dense clipped>
      <v-col class="text-right caption time-zone-notice">(times in UTC)</v-col>
      <v-row>
        <div
          class="add-event"
          style="--margtop: 0px; --margbot: 5px; --margrule: 20px; margin-left: 85px"
        >
          <div class="horiz-rule" />
          <div class="add-button">
            <v-btn compact small plain class="up-button">
              <v-icon small class="mr-1">mdi-plus-circle-outline</v-icon>Add event
            </v-btn>
          </div>
        </div>
      </v-row>
      <v-timeline-item
        v-for="event in sortedEvents"
        v-show="showItem(event)"
        :icon="iconItem(event)"
        :key="event.id"
        class="mb-4"
        :class="event.type == 'Custom event' ? 'custom-event' : null"
        color="blue"
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
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on" class="wavy-underline">{{
                  event.started_at | formatToUTC
                }}</span>
              </template>
              <span class="pre-formatted">{{ event.started_at | formatToTimeZones }}</span>
            </v-tooltip>
          </v-col>
        </v-row>
        <v-row>
          <div class="add-event" style="--margtop: -40px; --margbot: 0px; --margrule: 40px">
            <div class="horiz-rule" />
            <div class="add-button">
              <v-btn
                compact
                small
                plain
                class="up-button"
                @click="showNewEventDialog(event.started_at)"
              >
                <v-icon small class="mr-1">mdi-plus-circle-outline</v-icon>Add event
              </v-btn>
            </div>
          </div>
        </v-row>
        <div :v-if="event.type == 'Custom event'" style="" class="custom-event-edit">
          <v-btn plain small @click="showEditEventDialog(event)"><v-icon>mdi-pencil</v-icon></v-btn>
          <v-btn plain small @click="showDeleteEventDialog(event)">
            <v-icon>mdi-trash-can</v-icon>
          </v-btn>
        </div>
      </v-timeline-item>
    </v-timeline>
    <div v-else>
      <p class="text-center">No timeline data available.</p>
    </div>
    <div class="text-caption ml-10" v-if="countHidden() != 0">
      {{ "" + countHidden() }} event(s) are hidden due to current filter
    </div>
  </v-container>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import Util from "@/util"
import TimelineFilterDialog from "@/incident/TimelineFilterDialog.vue"
import EditEventDialog from "@/incident/EditEventDialog.vue"
import DeleteEventDialog from "@/incident/DeleteEventDialog.vue"

const eventTypeToIcon = {
  "Other": "mdi-monitor-star",
  "Field updated": "mdi-subtitles-outline",
  "Assessment updated": "mdi-priority-high",
  "Participant updated": "mdi-account-outline",
  "Custom event": "mdi-text-account",
}

const eventTypeToFilter = {
  "Other": "other_events",
  "Field updated": "field_updates",
  "Assessment updated": "assessment_updates",
  "Participant updated": "participant_updates",
  "Custom event": "user_curated_events",
}

export default {
  name: "IncidentTimelineTab",

  components: {
    TimelineFilterDialog,
    EditEventDialog,
    DeleteEventDialog,
  },

  data() {
    return {
      showDetails: false,
      exportLoading: false,
    }
  },

  computed: {
    ...mapFields("incident", ["selected.events", "selected.name", "timeline_filters"]),

    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
  },
  methods: {
    ...mapActions("incident", [
      "showNewEventDialog",
      "showEditEventDialog",
      "showDeleteEventDialog",
    ]),
    exportToCSV() {
      this.exportLoading = true
      let items = this.sortedEvents
      Util.exportCSV(items, this.name + "-timeline-export.csv")
      this.exportLoading = false
    },
    showItem(item) {
      if (item.description == "Incident created") return true
      return !this.timeline_filters[eventTypeToFilter[item.type]]
    },
    iconItem(item) {
      if (item.description == "Incident created") return "mdi-flare"
      return eventTypeToIcon[item.type]
    },
    countHidden() {
      if (!this.events) return 0
      return sum(
        this.events.map((e) => {
          return this.timeline_filters[eventTypeToFilter[e.type]] || false
        })
      )
    },
  },
}
</script>

<style scoped src="@/styles/timeline.css" />
