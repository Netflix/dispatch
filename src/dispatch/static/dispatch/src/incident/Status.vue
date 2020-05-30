<template>
  <v-app>
    <v-content>
      <v-card flat>
        <v-toolbar color="primary" extended flat height="150" />
        <v-card class="mx-auto" max-width="1000" style="margin-top: -64px;">
          <v-card-text>
            <div>Dispatch</div>
            <v-data-table
              :headers="headers"
              :items="items"
              :loading="loading"
              hide-default-footer
              loading-text="Loading... Please wait"
              :single-expand="singleExpand"
              :expanded.sync="expanded"
              show-expand
            >
              <template v-slot:top>
                <v-toolbar flat>
                  <v-toolbar-title>Active Security Incidents</v-toolbar-title>
                  <v-spacer></v-spacer>
                  <v-btn color="primary" dark class="mb-2" to="/incidents/report"
                    >Report an Incident</v-btn
                  >
                </v-toolbar>
              </template>
              <template v-slot:item.commander="{ item }">
                <a :href="item.commander.weblink" target="_blank" style="text-decoration: none;">
                  {{ item.commander.name }}
                  <v-icon small>open_in_new</v-icon>
                </a>
              </template>
              <template v-slot:item.id="{ item }">
                <v-btn x-small @click="joinIncident(item.id)">Join Incident</v-btn>
              </template>
              <template v-slot:expanded-item="{ headers, item }">
                <td :colspan="headers.length">
                  <v-container>
                    <v-row dense>
                      <v-col cols="12">
                        <v-card outlined>
                          <v-card-title class="title">Description</v-card-title>
                          <v-card-text>{{ item.description }}</v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                    <v-row dense>
                      <v-col cols="12">
                        <v-card outlined>
                          <v-card-text>
                            <div class="title text--primary">Last Tactical Report</div>
                            <div v-if="item.last_tactical_report">
                              <p>As of {{ item.last_tactical_report.created_at | formatDate }}</p>
                              <p class="subtitle-1 text--primary">Conditions</p>
                              <div>{{ item.last_tactical_report.details.conditions }}</div>
                              <p class="subtitle-1 text--primary">Actions</p>
                              <div>{{ item.last_tactical_report.details.actions }}</div>
                              <p class="subtitle-1 text--primary">Needs</p>
                              <div>{{ item.last_tactical_report.details.needs }}</div>
                            </div>
                            <div v-else>No tactical report available.</div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                    <v-row dense>
                      <v-col cols="12">
                        <v-card outlined>
                          <v-card-text>
                            <div class="title text--primary">Last Executive Report</div>
                            <div v-if="item.last_executive_report">
                              <p>As of {{ item.last_executive_report.created_at | formatDate }}</p>
                              <p class="subtitle-1 text--primary">Current Status</p>
                              <div>{{ item.last_executive_report.details.current_status }}</div>
                              <p class="subtitle-1 text--primary">Overview</p>
                              <div>{{ item.last_executive_report.details.overview }}</div>
                              <p class="subtitle-1 text--primary">Next Steps</p>
                              <div>{{ item.last_executive_report.details.next_steps }}</div>
                            </div>
                            <div v-else>No executive report available.</div>
                          </v-card-text>
                        </v-card>
                      </v-col>
                    </v-row>
                  </v-container>
                </td>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-card>
    </v-content>
    <!-- App Footer -->
    <v-footer height="auto" class="pa-3 app--footer">
      <span class="caption">Netflix Security &copy; {{ new Date().getFullYear() }}</span>
      <v-spacer />
      <span class="caption mr-1">Be Secure</span>
      <v-icon color="pink" small>favorite</v-icon>
    </v-footer>
  </v-app>
</template>

<script>
import { mapActions } from "vuex"
import IncidentApi from "@/incident/api"
export default {
  name: "IncidentStatus",

  data() {
    return {
      expanded: [],
      loading: false,
      singleExpand: true,
      items: [],
      headers: [
        { text: "Id", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Priority", value: "incident_priority.name", sortable: false },
        { text: "Type", value: "incident_type.name", sortable: false },
        { text: "Commander", value: "commander" },
        { text: "", value: "id" },
        { text: "", value: "data-table-expand" }
      ]
    }
  },

  mounted() {
    this.getActive()
  },

  methods: {
    getActive() {
      this.loading = true
      IncidentApi.getAll({ fields: ["status"], ops: ["=="], values: ["Active"] }).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    },
    ...mapActions("incident", ["joinIncident"])
  }
}
</script>
