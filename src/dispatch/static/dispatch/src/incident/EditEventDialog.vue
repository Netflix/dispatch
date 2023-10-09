<template>
  <v-dialog v-model="showEditEventDialog" persistent max-width="750px">
    <v-card>
      <v-card-title>
        <span v-if="uuid" class="text-h5">Create new event</span>
        <span v-else class="text-h5">Edit event</span>
      </v-card-title>
      <v-card-text>
        <v-container grid-list-md class="mt-3">
          <v-layout wrap>
            <v-row>
              <date-time-picker-menu
                label="Reported At"
                v-model="started_at"
                class="time-picker"
                :timezone="timezone"
              />
              <v-select
                v-model="timezone"
                label="Time zone"
                :items="timezones"
                class="ml-2 time-zone-select"
              />
              <v-btn color="green en-1" class="ml-10 mt-3" width="100" @click="setTimeToNow()">
                Now
              </v-btn>
            </v-row>
            <v-row>
              <span class="ml-8 time-utc"> Time in UTC is {{ formatToUTC(started_at) }} </span>
            </v-row>
            <v-flex xs12>
              <v-textarea
                v-model="description"
                class="mt-3"
                label="Description"
                hint="Description of the event."
                clearable
                required
              />
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="closeEditEventDialog()"> Cancel </v-btn>
        <v-btn v-if="uuid" color="green en-1" variant="text" @click="updateExistingEvent()">
          OK
        </v-btn>
        <v-btn v-else color="green en-1" variant="text" @click="storeNewEvent()"> OK </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatToUTC } from "@/filters"

import DateTimePickerMenu from "@/components/DateTimePickerMenu.vue"
import moment from "moment-timezone"

export default {
  name: "EditEventDialog",

  data() {
    return {
      timezones: ["UTC", "America/Los_Angeles"],
      timezone: "UTC",
    }
  },

  setup() {
    return { formatToUTC }
  },

  components: {
    DateTimePickerMenu,
  },

  computed: {
    ...mapFields("incident", [
      "dialogs.showEditEventDialog",
      "selected.currentEvent.started_at",
      "selected.currentEvent.description",
      "selected.currentEvent.uuid",
    ]),
  },

  methods: {
    ...mapActions("incident", ["closeEditEventDialog", "storeNewEvent", "updateExistingEvent"]),
    init() {
      const local_zone_name = moment.tz.guess() || "America/Los_Angeles"
      if (!this.timezones.includes(local_zone_name)) {
        this.timezones.push(local_zone_name)
      }
      this.timezone = local_zone_name
    },
    setTimeToNow() {
      this.eventStart = new Date()
    },
  },
  mounted() {
    this.init()
  },
}
</script>

<style scoped>
.time-picker {
  max-width: 500px;
}
.time-zone-select {
  max-width: 250px;
}

.time-utc {
  margin-top: -15px;
}
</style>
