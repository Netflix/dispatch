<template>
  <v-navigation-drawer v-model="showHistory" location="right" width="650">
    <template #prepend>
      <v-list-item lines="two">
        <v-list-item-title class="text-h6"> History </v-list-item-title>
        <v-list-item-subtitle>Signal Definition</v-list-item-subtitle>

        <template #append>
          <v-btn icon variant="text" color="secondary" @click="closeHistory()">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-list-item>
      <template v-if="events && events.length">
        <v-timeline density="compact" clipped class="signal-timeline">
          <v-timeline-item
            v-for="event in sortedEvents"
            :icon="iconItem(event)"
            :key="event.id"
            dot-color="blue"
            class="signal-event"
          >
            <template #icon>
              <v-icon color="white" />
            </template>
            <v-row justify="space-between">
              <v-col cols="8">
                {{ event.description }}
                <transition-group name="slide">
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
                  {{ event.owner }}
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
            <!-- <v-row>
              <div class="mb-8" />
            </v-row> -->
          </v-timeline-item>
        </v-timeline>
      </template>
      <div v-else>
        <p class="text-center">No timeline data available.</p>
      </div>
    </template>
  </v-navigation-drawer>
</template>
<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { snakeToCamel, formatToUTC, formatToTimeZones } from "@/filters"

export default {
  setup() {
    return { snakeToCamel, formatToUTC, formatToTimeZones }
  },

  name: "SignalHistoryDialog",

  computed: {
    ...mapFields("signal", ["dialogs.showHistory", "selected.events", "selected"]),

    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
  },

  methods: {
    ...mapActions("signal", ["save", "closeHistory"]),
    iconItem(event) {
      if (event.description == "Signal created") return "mdi-alert-plus-outline"
      if (event.description == "Signal deleted") return "mdi-alert-minute-outline"
      return "mdi-swap-horizontal"
    },
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>

<style scoped src="@/styles/timeline.css" />
