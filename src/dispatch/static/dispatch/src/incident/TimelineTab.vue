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
            <v-btn
              compact
              small
              plain
              class="up-button"
              @click="showNewPreEventDialog(sortedEvents[0].started_at)"
            >
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
        :class="classType(event)"
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
          <v-col cols="1">
            <div v-if="isEditable(event)" class="custom-event-edit">
              <v-btn plain small @click="showEditEventDialog(event)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <br />
              <v-btn plain small @click="togglePin(event)">
                <v-hover v-slot="{ hover }">
                  <v-icon v-if="!isPinned(event)">mdi-pin-outline</v-icon>
                  <v-icon v-else-if="hover && isPinned(event)">mdi-pin-off</v-icon>
                  <v-icon v-else-if="!hover && isPinned(event)">mdi-pin</v-icon>
                </v-hover>
              </v-btn>
              <br />
              <v-btn plain small @click="showDeleteEventDialog(event)">
                <v-icon>mdi-trash-can</v-icon>
              </v-btn>
            </div>
            <div v-if="isPinned(event) && !isEditable(event)" class="pinned-event">
              <v-btn plain small @click="togglePin(event)">
                <v-hover v-slot="{ hover }">
                  <v-icon v-if="hover">mdi-pin-off</v-icon>
                  <v-icon v-else>mdi-pin</v-icon>
                </v-hover>
              </v-btn>
            </div>
            <div v-if="isPinned(event) && isEditable(event)" class="pinned-custom-event">
              <v-btn plain small @click="togglePin(event)">
                <v-icon>mdi-pin</v-icon>
              </v-btn>
            </div>
            <div v-else-if="!isPinned(event) && !isEditable(event)" class="pinned-event">
              <v-btn plain small @click="togglePin(event)">
                <v-icon>mdi-pin-outline</v-icon>
              </v-btn>
            </div>
          </v-col>
          <v-col class="text-right" cols="4">
            <v-col>
              <v-tooltip bottom>
                <template #activator="{ on, attrs }">
                  <span v-bind="attrs" v-on="on" class="wavy-underline">{{
                    event.started_at | formatToUTC
                  }}</span>
                </template>
                <span class="pre-formatted">{{ event.started_at | formatToTimeZones }}</span>
              </v-tooltip>
            </v-col>
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
  Other: "mdi-monitor-star",
  "Field updated": "mdi-subtitles-outline",
  "Assessment updated": "mdi-priority-high",
  "Participant updated": "mdi-account-outline",
  "Custom event": "mdi-text-account",
  "Imported message": "mdi-page-next-outline",
}

const eventTypeToFilter = {
  Other: "other_events",
  "Field updated": "field_updates",
  "Assessment updated": "assessment_updates",
  "Participant updated": "participant_updates",
  "Custom event": "user_curated_events",
  "Imported message": "user_curated_events",
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
      "showNewPreEventDialog",
      "togglePin",
    ]),
    exportToCSV() {
      this.exportLoading = true
      const selected_items = []
      let items = this.sortedEvents
      items.forEach((item) => {
        if (this.showItem(item)) {
          selected_items.push(item)
        }
      })

      Util.exportCSV(
        selected_items.map((item) => ({
          "Time (in UTC)": item.started_at,
          Description: item.description,
          Owner: this.extractOwner(item),
        })),
        this.name + "-timeline-export.csv"
      )
      this.exportLoading = false
    },
    showItem(event) {
      if (event.pinned) return true
      return !this.timeline_filters[eventTypeToFilter[event.type]]
    },
    iconItem(event) {
      if (event.description == "Incident created") return "mdi-flare"
      return eventTypeToIcon[event.type]
    },
    extractOwner(event) {
      if (event.owner != null && event.owner != "") return event.owner
      return "Dispatch"
    },
    countHidden() {
      if (!this.events) return 0
      return sum(
        this.events.map((e) => {
          return this.timeline_filters[eventTypeToFilter[e.type]] || false
        })
      )
    },
    isEditable(event) {
      return event.type == "Custom event" || event.type == "Imported message"
    },
    classType(event) {
      if (event.type == "Custom event" || event.type == "Imported message") {
        return "custom-event"
      }
      return "pinned-event"
    },
    isPinned(event) {
      return event.pinned
    },
  },
}
</script>

<style scoped src="@/styles/timeline.css" />
