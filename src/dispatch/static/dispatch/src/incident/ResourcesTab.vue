<template>
  <v-list>
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
    <v-divider />
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
    <v-divider />
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
    <v-divider />
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
    <v-divider />
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
    <span v-if="(!ticket && ticketPluginEnabled) ||
      (!conference && conferencePluginEnabled) ||
      (!conversation && conversationPluginEnabled) ||
      (!storage && storagePluginEnabled) ||
      (!documents && documentPluginEnabled)
      ">
      <v-list-item @click="createAllResources()">
        <v-list-item-content>
          <v-list-item-title>Recreate Missing Resources</v-list-item-title>
          <v-list-item-subtitle>Initiate a retry for creating any missing or unsuccesfully created
            resource(s).</v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-action>
          <v-list-item-icon>
            <v-icon>refresh</v-icon>
          </v-list-item-icon>
        </v-list-item-action>
      </v-list-item>
    </span>
  </v-list>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

export default {
  name: "IncidentResourcesTab",

  data() {
    return {
      ticketPluginEnabled: false,
      conferencePluginEnabled: false,
      conversationPluginEnabled: false,
      storagePluginEnabled: false,
      documentPluginEnabled: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.ticket",
      "selected.storage",
      "selected.documents",
      "selected.conference",
      "selected.conversation",
    ]),
  },

  async mounted() {
    this.ticketPluginEnabled = await this.isPluginEnabled("ticket")
    this.conferencePluginEnabled = await this.isPluginEnabled("conference")
    this.conversationPluginEnabled = await this.isPluginEnabled("conversation")
    this.storagePluginEnabled = await this.isPluginEnabled("storage")
    this.documentPluginEnabled = await this.isPluginEnabled("document")
  },

  methods: {
    ...mapActions("incident", ["createAllResources", "isPluginEnabled"]),
  },
}
</script>
