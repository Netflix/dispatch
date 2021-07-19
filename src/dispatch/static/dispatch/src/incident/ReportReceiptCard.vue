<template>
  <v-card class="mx-auto ma-4" max-width="600" flat outlined>
    <v-card-text>
      <p class="display-2 text--primary">Incident Report</p>
      <p>
        This page will be populated with incident resources as they are created (if available). If
        you have any questions, please feel free to review the Frequently Asked Questions (FAQ)
        document linked below, and/or reach out to the listed Incident Commander.
      </p>
      <v-list three-line>
        <v-list-group :value="true">
          <template v-slot:activator>
            <v-list-item-title class="title"> Incident Details </v-list-item-title>
          </template>
          <v-list-item-group>
            <v-list-item
              :href="commander.individual.weblink"
              target="_blank"
              title="The Incident Commander is responsible for maintaining all necessary context and driving the incident to resolution."
            >
              <v-list-item-content>
                <v-list-item-title>Commander</v-list-item-title>
                <v-list-item-subtitle
                  >{{ commander.individual.name }} ({{
                    commander.individual.email
                  }})</v-list-item-subtitle
                >
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-divider />
            <v-list-item disabled>
              <v-list-item-content>
                <v-list-item-title>Title</v-list-item-title>
                <v-list-item-subtitle>{{ title }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <v-list-item disabled>
              <v-list-item-content>
                <v-list-item-title>Description</v-list-item-title>
                <v-list-item-subtitle>{{ description }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <v-list-item disabled>
              <v-list-item-content>
                <v-list-item-title>Project</v-list-item-title>
                <v-list-item-subtitle>{{ project.name }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <v-list-item disabled>
              <v-list-item-content>
                <v-list-item-title>Type</v-list-item-title>
                <v-list-item-subtitle>{{ incident_type.name }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <v-list-item disabled>
              <v-list-item-content>
                <v-list-item-title>Priority</v-list-item-title>
                <v-list-item-subtitle>{{ incident_priority.name }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <v-list-item disabled>
              <v-list-item-content>
                <v-list-item-title>Visibility</v-list-item-title>
                <v-list-item-subtitle>{{ visibility }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list-group>
      </v-list>
      <v-list three-line v-if="!trackingOnly">
        <v-list-group :value="true">
          <template v-slot:activator>
            <v-list-item-title class="title"> Incident Resources </v-list-item-title>
          </template>
          <span v-if="activeResourcePlugins.ticket">
            <v-list-item v-if="ticket" :href="ticket.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Ticket</v-list-item-title>
                <v-list-item-subtitle>{{ ticket.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-content>
                <v-list-item-title>Creating incident ticket...</v-list-item-title>
                <v-progress-linear indeterminate />
              </v-list-item-content>
            </v-list-item>
            <v-divider />
          </span>
          <span v-if="activeResourcePlugins.conference">
            <v-list-item v-if="conference" :href="conference.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Video Conference</v-list-item-title>
                <v-list-item-subtitle>{{ conference.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-content>
                <v-list-item-title>Creating incident video conference...</v-list-item-title>
                <v-progress-linear indeterminate />
              </v-list-item-content>
            </v-list-item>
            <v-divider />
          </span>
          <span v-if="activeResourcePlugins.conversation">
            <v-list-item v-if="conversation" :href="conversation.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Conversation</v-list-item-title>
                <v-list-item-subtitle>{{ conversation.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-content>
                <v-list-item-title>Creating incident conversation...</v-list-item-title>
                <v-progress-linear indeterminate />
              </v-list-item-content>
            </v-list-item>
            <v-divider />
          </span>
          <span v-if="activeResourcePlugins.storage">
            <v-list-item v-if="storage" :href="storage.weblink" target="_blank">
              <v-list-item-content>
                <v-list-item-title>Storage</v-list-item-title>
                <v-list-item-subtitle>{{ storage.description }}</v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-list-item-icon>
                  <v-icon>open_in_new</v-icon>
                </v-list-item-icon>
              </v-list-item-action>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-content>
                <v-list-item-title>Creating incident storage...</v-list-item-title>
                <v-progress-linear indeterminate />
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <span v-if="activeResourcePlugins.document">
              <span v-if="documents.length">
                <span v-for="document in documents" :key="document.resource_id">
                  <v-list-item :href="document.weblink" target="_blank">
                    <v-list-item-content>
                      <v-list-item-title>{{ document.resource_type | deslug }}</v-list-item-title>
                      <v-list-item-subtitle>{{ document.description }}</v-list-item-subtitle>
                    </v-list-item-content>
                    <v-list-item-action>
                      <v-list-item-icon>
                        <v-icon>open_in_new</v-icon>
                      </v-list-item-icon>
                    </v-list-item-action>
                  </v-list-item>
                  <v-divider />
                </span>
              </span>
              <span v-else>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Creating incident documents... </v-list-item-title>
                    <v-progress-linear indeterminate />
                  </v-list-item-content>
                </v-list-item>
              </span>
              <v-divider />
            </span>
          </span>
        </v-list-group>
      </v-list>
      <v-container grid-list-md>
        <v-flex xs12>
          <v-btn color="info" depressed @click="resetSelected()"> Report another incident </v-btn>
        </v-flex>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { forEach, find } from "lodash"
import PluginApi from "@/plugin/api"

export default {
  name: "ReportReceiptCard",

  components: {},
  data() {
    return {
      isSubmitted: false,
      activeResourcePlugins: {
        document: null,
        ticket: null,
        storage: null,
        conversation: null,
        conference: null,
      },
    }
  },
  created() {
    PluginApi.getAllInstances({
      itemsPerPage: -1,
      filter: JSON.stringify({
        and: [
          {
            model: "PluginInstance",
            field: "enabled",
            op: "==",
            value: "true",
          },
          {
            model: "Project",
            field: "name",
            op: "==",
            value: this.project.name,
          },
        ],
      }),
    }).then((response) => {
      let data = response.data.items
      let activeResourcePlugins = this.activeResourcePlugins
      forEach(Object.keys(activeResourcePlugins), function (value) {
        activeResourcePlugins[value] = find(data, function (o) {
          return o.plugin.type === value
        })
      })
    })
  },
  computed: {
    ...mapFields("incident", [
      "selected.incident_priority",
      "selected.incident_type",
      "selected.commander",
      "selected.title",
      "selected.tags",
      "selected.description",
      "selected.conversation",
      "selected.conference",
      "selected.visibility",
      "selected.storage",
      "selected.documents",
      "selected.project",
      "selected.trackingOnly",
      "selected.loading",
      "selected.ticket",
      "selected.id",
    ]),
  },

  methods: {
    ...mapActions("incident", ["report", "get", "resetSelected"]),
  },
}
</script>
