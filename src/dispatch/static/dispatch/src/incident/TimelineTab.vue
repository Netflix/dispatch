<template>
  <v-tab-item key="timeline">
    <v-container>
      <v-timeline dense clipped>
        <v-timeline-item v-for="event in events" :key="event.id" class="mb-4" color="blue" small>
          <v-row justify="space-between">
            <v-col cols="7">
              {{ event.description }}
              <div class="caption">{{ event.source }}</div>
            </v-col>
            <v-col class="text-right" cols="5">{{ event.started_at | formatDate }}</v-col>
          </v-row>
        </v-timeline-item>
      </v-timeline>
    </v-container>
  </v-tab-item>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "IncidentTimelineTab",
  computed: {
    ...mapFields("incident", ["selected.events"])
  }
}
</script>
