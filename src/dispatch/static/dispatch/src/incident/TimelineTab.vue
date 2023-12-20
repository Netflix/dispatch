<template>
  <v-container>
    <v-row justify="end" class="align-items-baseline">
      <v-switch v-model="showDetails" label="Show details" class="flex-grow-0" />

      <timeline-export-dialog :showItem="showItem" :extractOwner="extractOwner" />
      <timeline-filter-dialog ref="filter_dialog" />

      <edit-event-dialog v-if="showEditEventDialog" />
      <delete-event-dialog />
    </v-row>
    <template v-if="events && events.length">
      <v-timeline density="compact" clipped>
        <v-timeline-item hide-dot>
          <v-row>
            <v-col class="text-right text-caption time-zone-notice">(times in UTC)</v-col>
            <div class="add-event" style="--margtop: 0px; --margbot: 5px; --margrule: 20px">
              <div class="horiz-rule" />
              <div class="add-button">
                <v-btn
                  compact
                  size="small"
                  variant="plain"
                  class="up-button"
                  @click="showNewPreEventDialog(sortedEvents[0].started_at)"
                >
                  <v-icon size="small" class="mr-1">mdi-plus-circle-outline</v-icon>Add event
                </v-btn>
              </div>
            </div>
          </v-row>
        </v-timeline-item>
        <v-timeline-item
          v-for="event in sortedEvents"
          v-show="showItem(event)"
          :icon="iconItem(event)"
          :key="event.id"
          class="mb-4"
          :class="classType(event)"
          dot-color="blue"
        >
          <template #icon>
            <v-icon color="white" />
          </template>
          <v-row justify="space-between">
            <v-col cols="7">
              {{ event.description }}
              <transition-group name="slide" v-if="showDetails">
                <template v-for="(value, key) in event.details" :key="key">
                  <v-card>
                    <v-card-title class="text-subtitle-1">
                      {{ snakeToCamel(key) }}
                    </v-card-title>
                    <v-card-text>{{ value }}</v-card-text>
                  </v-card>
                </template>
              </transition-group>
              <div class="text-caption">
                {{ event.source }}
              </div>
            </v-col>
            <v-col cols="1">
              <div v-if="isEditable(event)" class="custom-event-edit">
                <v-btn variant="plain" @click="showNewEditEventDialog(event)">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <br />
                <v-btn variant="plain" @click="togglePin(event)">
                  <v-hover v-slot="{ isHovering, props }">
                    <v-icon v-if="!isPinned(event)" v-bind="props">mdi-pin-outline</v-icon>
                    <v-icon v-else-if="isHovering && isPinned(event)" v-bind="props">
                      mdi-pin-off
                    </v-icon>
                    <v-icon v-else-if="!isHovering && isPinned(event)" v-bind="props">
                      mdi-pin
                    </v-icon>
                  </v-hover>
                </v-btn>
                <br />
                <v-btn variant="plain" @click="showDeleteEventDialog(event)">
                  <v-icon>mdi-trash-can</v-icon>
                </v-btn>
              </div>
              <div v-if="isPinned(event) && !isEditable(event)" class="pinned-event">
                <v-btn variant="plain" @click="togglePin(event)">
                  <v-hover v-slot="{ isHovering, props }">
                    <v-icon v-if="isHovering" v-bind="props">mdi-pin-off</v-icon>
                    <v-icon v-else v-bind="props">mdi-pin</v-icon>
                  </v-hover>
                </v-btn>
              </div>
              <div v-if="isPinned(event) && isEditable(event)" class="pinned-custom-event">
                <v-btn variant="plain" @click="togglePin(event)">
                  <v-icon>mdi-pin</v-icon>
                </v-btn>
              </div>
              <div v-else-if="!isPinned(event) && !isEditable(event)" class="pinned-event">
                <v-btn variant="plain" @click="togglePin(event)">
                  <v-icon>mdi-pin-outline</v-icon>
                </v-btn>
              </div>
            </v-col>
            <v-col class="text-right" cols="4">
              <v-col>
                <v-tooltip location="bottom">
                  <template #activator="{ props }">
                    <span v-bind="props" class="wavy-underline">{{
                      formatToUTC(event.started_at)
                    }}</span>
                  </template>
                  <span class="pre-formatted">{{ formatToTimeZones(event.started_at) }}</span>
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
                  size="small"
                  variant="plain"
                  class="up-button"
                  @click="showNewEventDialog(event.started_at)"
                >
                  <v-icon size="small" class="mr-1">mdi-plus-circle-outline</v-icon>Add event
                </v-btn>
              </div>
            </div>
          </v-row>
        </v-timeline-item>
      </v-timeline>
    </template>
    <div v-else>
      <p class="text-center">No timeline data available.</p>
    </div>
    <div class="text-caption ml-3 mt-10" v-if="countHidden() !== 0">
      {{ "" + countHidden() }} event(s) are hidden due to current filter
    </div>
  </v-container>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import { snakeToCamel, formatToUTC, formatToTimeZones } from "@/filters"

import TimelineFilterDialog from "@/incident/TimelineFilterDialog.vue"
import TimelineExportDialog from "./TimelineExportDialog.vue"
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
    TimelineExportDialog,
  },

  data() {
    return {
      showDetails: false,
    }
  },

  setup() {
    return { snakeToCamel, formatToUTC, formatToTimeZones }
  },

  computed: {
    ...mapFields("incident", [
      "selected.events",
      "selected.name",
      "timeline_filters",
      "dialogs.showEditEventDialog",
    ]),

    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
  },
  methods: {
    ...mapActions("incident", [
      "showNewEventDialog",
      "showNewEditEventDialog",
      "showDeleteEventDialog",
      "showNewPreEventDialog",
      "togglePin",
    ]),
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
    showItem(event) {
      if (event.pinned) {
        return true
      }
      return !this.timeline_filters[eventTypeToFilter[event.type]]
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
