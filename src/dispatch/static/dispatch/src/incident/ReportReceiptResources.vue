<template>
  <v-container>
    <v-row dense>
      <v-col cols="12">
        <v-card>
          <v-list-item lines="two">
            <v-list-item-title class="text-h6"> Incident Details </v-list-item-title>
          </v-list-item>
          <v-card-text>
            <v-row align="center">
              <v-col class="text-h5" cols="12"> {{ title }} </v-col>
            </v-row>
          </v-card-text>

          <v-list class="bg-transparent">
            <v-list-item>
              <v-list-item-title>Type</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ incident_type.name }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Priority</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                <incident-priority :priority="incident_priority.name" />
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Visibility</v-list-item-title>
              <v-list-item-subtitle class="text-right"> {{ visibility }} </v-list-item-subtitle>
            </v-list-item>
          </v-list>

          <v-divider />

          <v-card-actions>
            <v-list-item class="grow">
              <template #prepend>
                <v-avatar color="grey-darken-3">
                  <span class="text-white text-h5">{{ initials(commander.individual.name) }}</span>
                </v-avatar>
              </template>

              <v-list-item-title>{{ commander.individual.name }}</v-list-item-title>
              <v-list-item-subtitle>Incident Commander</v-list-item-subtitle>

              <template #append>
                <v-btn
                  v-if="commander.individual.phone"
                  :href="'tel:' + commander.individual.phone"
                  icon
                  variant="text"
                  class="mr-1"
                >
                  <v-icon>mdi-phone</v-icon>
                </v-btn>
                <v-btn
                  :href="'mailto:' + commander.individual.email"
                  icon
                  variant="text"
                  class="mr-1"
                >
                  <v-icon>mdi-email</v-icon>
                </v-btn>
              </template>
            </v-list-item>
          </v-card-actions>
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card>
          <v-list-item lines="two">
            <v-list-item-title class="text-h6"> Incident Resources </v-list-item-title>
          </v-list-item>
          <span v-for="pluginInstance in activeResourcePlugins" :key="pluginInstance.id">
            <span v-if="pluginInstance.plugin.type === 'document'">
              <span v-if="resourceData('documents').length">
                <span v-for="document in resourceData('documents')" :key="document.resource_id">
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
                  <v-list-item-title>Creating documents... </v-list-item-title>
                  <v-progress-linear indeterminate />
                </v-list-item>
              </span>
            </span>
            <span v-else>
              <v-list-item
                v-if="resourceData(pluginInstance.plugin.type)"
                target="_blank"
                :href="resourceData(pluginInstance.plugin.type).weblink"
              >
                <v-list-item-title>{{ capitalize(pluginInstance.plugin.type) }}</v-list-item-title>
                <v-list-item-subtitle>{{
                  resourceData(pluginInstance.plugin.type).description
                }}</v-list-item-subtitle>

                <template #append>
                  <v-icon>mdi-open-in-new</v-icon>
                </template>
              </v-list-item>
              <v-list-item v-else>
                <v-list-item-title
                  >Creating {{ pluginInstance.plugin.type }} resource...</v-list-item-title
                >
                <v-progress-linear indeterminate />
              </v-list-item>
              <v-divider />
            </span>
          </span>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { initials, deslug, capitalize } from "@/filters"

import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import PluginApi from "@/plugin/api"

export default {
  name: "ReportReceiptCard",

  components: {
    IncidentPriority,
  },
  data() {
    return {
      isSubmitted: false,
      resourcePlugins: ["document", "ticket", "storage", "conversation", "conference"],
      activeResourcePlugins: [],
      project_faq: null,
    }
  },
  setup() {
    return { initials, deslug, capitalize }
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
      response.data.items.forEach((item) => {
        if (this.resourcePlugins.includes(item.plugin.type)) {
          this.activeResourcePlugins.push(item)
        }
      })
    })
  },
  computed: {
    ...mapFields("incident", [
      "selected",
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
      "selected.loading",
      "selected.ticket",
      "selected.id",
    ]),
  },

  methods: {
    ...mapActions("incident", ["report", "get", "resetSelected"]),
    resourceData(pluginType) {
      return this.selected[pluginType]
    },
  },
}
</script>
