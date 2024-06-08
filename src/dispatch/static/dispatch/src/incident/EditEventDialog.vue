<template>
  <v-dialog v-model="showEditEventDialog" persistent max-width="750px">
    <v-card>
      <v-card-title>
        <span v-if="uuid" class="text-h5">Edit event</span>
        <span v-else class="text-h5">Create new event</span>
      </v-card-title>
      <v-card-text>
        <v-container class="mt-3">
          <v-row>
            <v-col cols="5">
              <date-time-picker-menu
                label="Reported At"
                v-model="started_at"
                class="time-picker"
                :timezone="timezone"
                @update:model-value="update_started_at"
              />
              <span
                class="ml-10 time-utc text-caption"
                style="position: absolute; margin-top: -20px"
              >
                Time in UTC is {{ formatToUTC(started_at_in_utc) }}
              </span>
            </v-col>
            <v-col cols="5">
              <v-select
                v-model="timezone"
                label="Time zone"
                :items="timezones"
                class="ml-2 time-zone-select"
              />
            </v-col>
            <v-col cols="1">
              <v-btn color="green en-1" class="ml-10 mt-3" width="100" @click="setTimeToNow()">
                Now
              </v-btn>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-textarea
                v-model="description"
                class="mt-3"
                label="Description"
                hint="Description of the event."
                clearable
                required
              />
            </v-col>
          </v-row>
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
      started_at_in_utc: "",
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
    update_started_at(val) {
      this.started_at = val
      this.started_at_in_utc = val
    },
  },
  mounted() {
    this.init()
    this.started_at_in_utc = this.started_at
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
