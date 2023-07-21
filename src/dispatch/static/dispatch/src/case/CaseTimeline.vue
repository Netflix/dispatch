<template>
  <v-container>
    <v-timeline v-if="events && events.length" dense class="ml-n12">
      <v-timeline-item v-for="event in sortedEvents" :key="event.id" color="rgb(9, 19, 40)" small>
        <div class="caption">
          {{ event.source }}
        </div>
        <div class="text-right caption mt-n4">
          {{ event.started_at }}
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
import { mapFields } from "vuex-map-fields"

import UserApi from "@/auth/api"

export default {
  name: "CaseTimeline",

  data() {
    return {
      showDetails: false,
      exportLoading: false,
      input: null,
      nonce: 0,
    }
  },

  created() {
    UserApi.getUserInfo().then((response) => {
      this.user = response.data
      console.log(this.user)
    })
  },

  computed: {
    ...mapFields("case_management", ["selected.events", "selected.name"]),

    sortedEvents: function () {
      this.events = this.events
        .slice()
        .sort((a, b) => new Date(a.started_at) - new Date(b.started_at))

      return this.events.slice().reverse()
    },

    methods: {
      comment() {
        const time = new Date().toTimeString()
        this.events.push({
          id: this.nonce++,
          text: this.input,
          time: time.replace(/:\d{2}\sGMT-\d{4}\s\((.*)\)/, (match, contents, offset) => {
            return ` ${contents
              .split(" ")
              .map((v) => v.charAt(0))
              .join("")}`
          }),
        })

        this.input = null
      },
    },
  },
}
</script>

<style>
.v-alert.outlined {
  border: 1px dotted rgb(188, 188, 188) !important;
}

.highlighted-chip {
  background: linear-gradient(45deg, #5252ff 0%, #fad0c4 99%, #fad0c4 100%) !important;
}
</style>
