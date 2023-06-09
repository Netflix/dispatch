<template>
  <v-container>
    <v-timeline v-if="events && events.length" dense class="ml-n12">
      <v-timeline-item
        v-for="event in sortedEvents"
        :key="event.id"
        class="mb-4"
        color="red lighten-4"
        small
      >
        <div class="caption">
          {{ event.source }}
        </div>
        <v-alert :value="true" color="grey lighten-4" class="black--text outlined">
          <v-row>
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
            </v-col>
            <v-col class="text-right" cols="5">
              {{ event.started_at | formatRelativeDate }}
            </v-col>
          </v-row>
        </v-alert>
      </v-timeline-item>
    </v-timeline>
    <div v-else>
      <p class="text-center">No timeline data available.</p>
    </div>
  </v-container>
</template>

<script>
export default {
  name: "CaseTimeline",

  props: {
    events: {
      type: Array,
      required: true,
    },
    caseName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      showDetails: false,
      exportLoading: false,
    }
  },

  computed: {
    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
  },
}
</script>

<style>
.v-alert.outlined {
  border: 1px dotted rgb(188, 188, 188) !important;
}
</style>
