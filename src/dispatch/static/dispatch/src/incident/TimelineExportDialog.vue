<template>
  <div class="d-flex justify-space-around">
    <v-menu>
      <template #activator="{ props }">
        <v-btn color="secondary" class="ml-2 mr-2 mt-3" v-bind="props"> Export </v-btn>
      </template>
      <v-list>
        <v-list-item @click="exportAsCSV()">Export to CSV </v-list-item>
        <v-list-item @click="showExportDialog = true">Export to Doc </v-list-item>
      </v-list>
    </v-menu>

    <v-dialog v-model="showExportDialog" persistent max-width="800px">
      <v-card>
        <v-card-title>
          <span class="text-h5" style="margin-bottom: 10px">Export Timeline Events</span>
        </v-card-title>

        <v-card-subtitle class="subtitle_top">
          Exports the current filtered timeline events directly into a document
        </v-card-subtitle>

        <v-card-text>
          <v-card class="rounded-0">
            <div class="ml-5 mt-5 text-grey">Select incident document(s) for export</div>
            <v-checkbox label="Incident Document" v-model="incidentDocument" class="ml-5" />
            <v-checkbox
              class="ml-5"
              style="margin-top: -30px"
              v-if="!isActive()"
              label="Review Document"
              v-model="reviewDocument"
            />
            <div
              class="ml-8 mb-2 bg-error text-caption"
              v-if="!incidentDocument && !reviewDocument"
            >
              At least one must be selected
            </div>
          </v-card>
          <v-checkbox class="mt-3" label="Also export Owner field" v-model="exportOwner" />
          <v-select
            v-model="timezone"
            label="Time zone"
            style="margin-top: -20px"
            :items="timezones"
            class="ml-2 time-zone-select"
          />
        </v-card-text>

        <div class="note-message font-weight-bold">
          Note: Exporting events will overwrite the table under Timeline in the document(s).
        </div>

        <v-card-actions>
          <v-spacer />
          <v-btn color="red en-1" variant="text" @click="cancel()"> Cancel </v-btn>
          <v-btn
            color="blue en-1"
            variant="text"
            @click="handleDocExport()"
            :disabled="!incidentDocument && !reviewDocument"
          >
            Submit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import Util from "@/util"
import moment from "moment-timezone"
const eventTypeToFilter = {
  Other: "other_events",
  "Field updated": "field_updates",
  "Assessment updated": "assessment_updates",
  "Participant updated": "participant_updates",
  "Custom event": "user_curated_events",
  "Imported message": "user_curated_events",
}

export default {
  // data: () => ({
  //   items: [{ title: "Click Me" }, { title: "Click Me1" }],
  // }),
  name: "TimelineExportDialog",
  props: {
    showItem: Function,
    extractOwner: Function,
  },

  data() {
    return {
      incidentDocument: true,
      reviewDocument: false,
      showExportDialog: false,
      timezones: ["UTC", "America/Los_Angeles"],
      timezone: "UTC",
      user_timeline_filters: {},
      exportOwner: false,
    }
  },
  computed: {
    ...mapFields("incident", [
      "selected.events",
      "selected.name",
      "timeline_filters",
      "selected.status",
    ]),

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
      if (this.status == "Active") {
        return true
      }
      return false
    },
    handleDocExport() {
      let user_timeline_filters = this.getUserFilters()
      user_timeline_filters["incidentDocument"] = this.incidentDocument
      user_timeline_filters["reviewDocument"] = this.reviewDocument
      user_timeline_filters["timezone"] = this.timezone
      user_timeline_filters["exportOwner"] = this.exportOwner
      this.$store.dispatch("incident/exportDoc", user_timeline_filters)
      this.showExportDialog = false
    },

    getUserFilters() {
      for (const key in eventTypeToFilter) {
        if (this.timeline_filters[eventTypeToFilter[key]] === true) {
          this.user_timeline_filters[key] = false
        } else {
          this.user_timeline_filters[key] = true
        }
      }
      return this.user_timeline_filters
    },
  },
}
</script>
<style>
.note-message {
  color: rgb(243, 89, 89);
  margin-left: 30px;
  margin-bottom: 10px;
}
.error {
  color: rgb(243, 89, 89);
  margin-top: -30px;
}
</style>
