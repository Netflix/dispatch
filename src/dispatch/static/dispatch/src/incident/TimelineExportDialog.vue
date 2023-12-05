<template>
  <div class="d-flex justify-space-around">
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn color="secondary" class="ml-2 mr-2 mt-3" v-bind="props"> Export </v-btn>
      </template>
      <v-list>
        <v-list-item @click="exportAsCSV()">Export to CSV </v-list-item>
        <v-list-item @click="showExportDialog = true">Export to Doc </v-list-item>
      </v-list>
    </v-menu>

    <v-dialog v-model="showExportDialog" max-width="800px">
      <v-card>
        <v-card-title>
          <span class="headline" style="margin-bottom: 10px;">Export Timeline Events</span>
        </v-card-title>

        <v-card-subtitle class="subtitle_top">
          Select the document & timezone to export the events
        </v-card-subtitle>

        <v-card-text>
          <v-checkbox label="Incident Document" v-model="incidentDocument"></v-checkbox>
          <v-checkbox v-if="isActive() == false" label="Review Document" v-model="reviewDocument"></v-checkbox>
          <v-select v-model="timezone" label="Time zone" :items="timezones" class="ml-2 time-zone-select" />
        </v-card-text>

        <div class="note-message"> Note: Exporting events will overwrite the table under Timeline in the document(s).
        </div>

        <v-card-actions>
          <v-btn color="info" text @click="handleDocExport()"> Submit </v-btn>
          <v-btn color="info" text @click="cancel()"> Cancel </v-btn>
        </v-card-actions>

      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import Util from "@/util"
const eventTypeToFilter = {
  Other: "other_events",
  "Field updated": "field_updates",
  "Assessment updated": "assessment_updates",
  "Participant updated": "participant_updates",
  "Custom event": "user_curated_events",
  "Imported message": "user_curated_events",
}

export default {
  data: () => ({
    items: [
      { title: 'Click Me' },
      { title: 'Click Me1' },
    ],
  }),
  name: "TimelineExportDialog",
  props: {
    showItem: Function,
    extractOwner: Function
  },


  data() {
    return {
      incidentDocument: false,
      reviewDocument: false,
      showExportDialog: false,
      timezones: ["UTC", "America/Los_Angeles"],
      timezone: "UTC",
      user_timeline_filters: {},
    }
  },
  computed: {
    ...mapFields("incident", ["selected.events", "selected.name", "timeline_filters", "selected.status"]),

    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
  },

  methods: {
    ...mapActions("incident", ["getAll"]),
    cancel() {
      this.showExportDialog = false
    },
    exportAsCSV() {
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

    },
    init() {
      const local_zone_name = moment.tz.guess() || "America/Los_Angeles"
      if (!this.timezones.includes(local_zone_name)) {
        this.timezones.push(local_zone_name)
      }
      this.timezone = local_zone_name
    },
    mounted() {
      this.init()
    },
    isActive() {
      if (this.status == 'Active') {
        return true
      }
      return false
    },
    handleDocExport() {
      let user_timeline_filters = this.getUserFilters()
      user_timeline_filters['incidentDocument'] = this.incidentDocument
      user_timeline_filters['reviewDocument'] = this.reviewDocument
      user_timeline_filters['timezone'] = this.timezone
      this.$store.dispatch("incident/exportDoc", user_timeline_filters)
      this.showExportDialog = false
    },

    getUserFilters() {
      for (const key in eventTypeToFilter) {
        if (this.timeline_filters[eventTypeToFilter[key]] === true) {
          this.user_timeline_filters[key] = false;
        }
        else {
          this.user_timeline_filters[key] = true;
        }
      }
      return this.user_timeline_filters
    },
  }

}
</script>
<style>
.note-message {
  color: rgb(243, 89, 89);
  margin-left: 30px;
  margin-bottom: 10px;
}
</style>