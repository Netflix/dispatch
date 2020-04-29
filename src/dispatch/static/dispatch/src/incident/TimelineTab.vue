<template>
  <v-container>
    <v-timeline dense clipped>
      <v-timeline-item
        v-for="event in events"
        v-bind:key="event.id"
        class="mb-4"
        color="blue"
        small
      >
        <v-row justify="space-between">
          <v-col cols="7" @click="show = !show">
            {{ event.description }}
            <transition-group name="slide" v-if="show">
              <template v-for="(value, key) in event.details">
                <v-list v-bind:key="key">
                  <v-list-item-content>
                    <v-list-item-title>{{ key | capitalize }}</v-list-item-title>
                    <v-list-item-subtitle>{{ value }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list>
              </template>
            </transition-group>
            <div class="caption">{{ event.source }}</div>
          </v-col>
          <v-col class="text-right" cols="5">{{ event.started_at | formatDate }}</v-col>
        </v-row>
      </v-timeline-item>
    </v-timeline>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "IncidentTimelineTab",

  data() {
    return {
      show: false
    }
  },

  computed: {
    ...mapFields("incident", ["selected.events"])
  }
}
</script>
