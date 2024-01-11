<template>
  <v-card class="mx-auto ma-4" variant="outlined" title="Incident Report" max-width="600">
    <v-card-text>
      <p>
        This page will be populated with incident resources as they are created (if available). If
        you have any questions, please feel free to review the Frequently Asked Questions (FAQ)
        document linked below, and/or reach out to the listed Incident Commander.
      </p>
      <p v-if="project_faq">
        Checkout this project's incident FAQ document:
        <a :href="project_faq.weblink" target="_blank" style="text-decoration: none">
          {{ project_faq.name }}
          <v-icon size="small">mdi-open-in-new</v-icon>
        </a>
      </p>
      <v-list lines="three" :opened="[0]">
        <v-list-group :value="0">
          <template #activator="{ props }">
            <v-list-item v-bind="props">
              <v-list-item-title class="text-h6"> Incident Details </v-list-item-title>
            </v-list-item>
          </template>
          <v-list-item>
            <v-list-item-title>Title</v-list-item-title>
            <v-list-item-subtitle>{{ title }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Description</v-list-item-title>
            <v-list-item-subtitle>{{ description }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Project</v-list-item-title>
            <v-list-item-subtitle>{{ project.name }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Type</v-list-item-title>
            <v-list-item-subtitle>{{ incident_type.name }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Priority</v-list-item-title>
            <v-list-item-subtitle>{{ incident_priority.name }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Visibility</v-list-item-title>
            <v-list-item-subtitle>{{ visibility }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Incident Commander</v-list-item-title>
            <v-list-item-subtitle>
              <participant :participant="commander" />
            </v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Incident Commander Paged?</v-list-item-title>
            <v-list-item-subtitle>
              <span v-if="incident_priority.page_commander">
                The incident commander was paged.
              </span>
              <span v-else>The incident commander was not paged.</span>
            </v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item>
            <v-list-item-title>Incident Participants</v-list-item-title>
            <v-list-item-subtitle>
              <v-chip-group column>
                <template v-for="participant in participants" :key="participant.id">
                  <participant :participant="participant" />
                </template>
              </v-chip-group>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list-group>
      </v-list>
      <v-list lines="three" :opened="[0]">
        <v-list-group :value="0">
          <template #activator="{ props }">
            <v-list-item v-bind="props">
              <v-list-item-title class="text-h6"> Incident Resources </v-list-item-title>
            </v-list-item>
          </template>
          <span v-if="activeResourcePlugins.ticket">
            <v-list-item v-if="ticket" :href="ticket.weblink" target="_blank">
              <v-list-item-title>Ticket</v-list-item-title>
              <v-list-item-subtitle>{{ ticket.description }}</v-list-item-subtitle>

              <template #append>
                <v-icon>mdi-open-in-new</v-icon>
              </template>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-title>Creating incident ticket...</v-list-item-title>
              <v-progress-linear indeterminate />
            </v-list-item>
            <v-divider />
          </span>
          <span v-if="activeResourcePlugins.conference">
            <v-list-item v-if="conference" :href="conference.weblink" target="_blank">
              <v-list-item-title>Video Conference</v-list-item-title>
              <v-list-item-subtitle>{{ conference.description }}</v-list-item-subtitle>

              <template #append>
                <v-icon>mdi-open-in-new</v-icon>
              </template>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-title>Creating incident video conference...</v-list-item-title>
              <v-progress-linear indeterminate />
            </v-list-item>
            <v-divider />
          </span>
          <span v-if="activeResourcePlugins.conversation">
            <v-list-item v-if="conversation" :href="conversation.weblink" target="_blank">
              <v-list-item-title>Conversation</v-list-item-title>
              <v-list-item-subtitle>{{ conversation.description }}</v-list-item-subtitle>

              <template #append>
                <v-icon>mdi-open-in-new</v-icon>
              </template>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-title>Creating incident conversation...</v-list-item-title>
              <v-progress-linear indeterminate />
            </v-list-item>
            <v-divider />
          </span>
          <span v-if="activeResourcePlugins.storage">
            <v-list-item v-if="storage" :href="storage.weblink" target="_blank">
              <v-list-item-title>Storage</v-list-item-title>
              <v-list-item-subtitle>{{ storage.description }}</v-list-item-subtitle>

              <template #append>
                <v-icon>mdi-open-in-new</v-icon>
              </template>
            </v-list-item>
            <v-list-item v-else>
              <v-list-item-title>Creating incident storage...</v-list-item-title>
              <v-progress-linear indeterminate />
            </v-list-item>
            <v-divider />
            <span v-if="activeResourcePlugins.document">
              <span v-if="documents.length">
                <span v-for="document in documents" :key="document.resource_id">
                  <v-list-item :href="document.weblink" target="_blank">
                    <v-list-item-title>{{ deslug(document.resource_type) }}</v-list-item-title>
                    <v-list-item-subtitle>{{ document.description }}</v-list-item-subtitle>

                    <template #append>
                      <v-icon>mdi-open-in-new</v-icon>
                    </template>
                  </v-list-item>
                  <v-divider />
                </span>
              </span>
              <span v-else>
                <v-list-item>
                  <v-list-item-title>Creating incident documents... </v-list-item-title>
                  <v-progress-linear indeterminate />
                </v-list-item>
              </span>
              <v-divider />
            </span>
          </span>
        </v-list-group>
      </v-list>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="info" block variant="flat" @click="resetSelected()">
        Report Another Incident
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { forEach, find } from "lodash"
import { deslug } from "@/filters"
import DocumentApi from "@/document/api"
import Participant from "@/incident/Participant.vue"

import PluginApi from "@/plugin/api"

export default {
  name: "ReportReceiptCard",

  components: {
    Participant,
  },
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
      project_faq: null,
    }
  },
  setup() {
    return { deslug }
  },
  created() {
    this.getFAQ()
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
      "selected.participants",
      "selected.title",
      "selected.tags",
      "selected.description",
      "selected.conversation",
      "selected.conference",
      "selected.visibility",
      "selected.storage",
      "selected.documents",
      "selected.project",
      "selected.loading",
      "selected.ticket",
      "selected.id",
    ]),
  },

  methods: {
    getFAQ() {
      DocumentApi.getAll({
        filter: JSON.stringify({
          and: [
            {
              field: "resource_type",
              op: "==",
              value: "dispatch-faq-reference-document",
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
        if (response.data && response.data.items.length) {
          this.project_faq = response.data.items[0]
        }
      })
    },
    ...mapActions("incident", ["report", "get", "resetSelected"]),
  },
}
</script>
