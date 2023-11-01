<template>
  <v-list>
    <v-list-item v-if="ticket" :href="ticket.weblink" target="_blank" class="my-3">
      <v-list-item-title>Ticket</v-list-item-title>
      <v-list-item-subtitle>{{ ticket.description }}</v-list-item-subtitle>

      <template #append>
        <v-icon>mdi-open-in-new</v-icon>
      </template>
    </v-list-item>
    <v-divider />
    <v-list-item v-if="conference" :href="conference.weblink" target="_blank" class="my-3">
      <v-list-item-title>Video Conference</v-list-item-title>
      <v-list-item-subtitle>{{ conference.description }}</v-list-item-subtitle>

      <template #append>
        <v-icon>mdi-open-in-new</v-icon>
      </template>
    </v-list-item>
    <v-divider />
    <v-list-item v-if="conversation" :href="conversation.weblink" target="_blank" class="my-3">
      <v-list-item-title>Conversation</v-list-item-title>
      <v-list-item-subtitle>{{ conversation.description }}</v-list-item-subtitle>

      <template #append>
        <v-icon>mdi-open-in-new</v-icon>
      </template>
    </v-list-item>
    <v-divider />
    <v-list-item v-if="storage" :href="storage.weblink" target="_blank" class="my-3">
      <v-list-item-title>Storage</v-list-item-title>
      <v-list-item-subtitle>{{ storage.description }}</v-list-item-subtitle>

      <template #append>
        <v-icon>mdi-open-in-new</v-icon>
      </template>
    </v-list-item>
    <v-divider />
    <span v-for="document in documents" :key="document.resource_id">
      <v-list-item :href="document.weblink" target="_blank" class="my-3">
        <v-list-item-title>{{ deslug(document.resource_type) }}</v-list-item-title>
        <v-list-item-subtitle>{{ document.description }}</v-list-item-subtitle>

        <template #append>
          <v-icon>mdi-open-in-new</v-icon>
        </template>
      </v-list-item>
      <v-divider />
    </span>
    <span
      v-if="
        (!ticket && ticketPluginEnabled) ||
        (!conference && conferencePluginEnabled) ||
        (!conversation && conversationPluginEnabled) ||
        (!storage && storagePluginEnabled) ||
        (!documents && documentPluginEnabled)
      "
    >
      <v-list-item v-if="!loading" @click="createAllResources()" class="my-3">
        <v-list-item-title>Recreate Missing Resources</v-list-item-title>
        <v-list-item-subtitle
          >Initiate a retry for creating any missing or unsuccesfully created
          resource(s).</v-list-item-subtitle
        >
        <template #append>
          <v-icon>refresh</v-icon>
        </template>
      </v-list-item>
      <v-list-item v-else-if="loading" class="my-3">
        <v-list-item-title>Creating resources...</v-list-item-title>
        <v-list-item-subtitle
          >Initiate a retry for creating any missing or unsuccesfully created
          resource(s).</v-list-item-subtitle
        >
      </v-list-item>
    </span>
  </v-list>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { deslug } from "@/filters"

export default {
  name: "IncidentResourcesTab",

  setup() {
    return { deslug }
  },

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
      "selected.conference",
      "selected.conversation",
      "selected.documents",
      "selected.loading",
      "selected.storage",
      "selected.ticket",
    ]),
  },

  async mounted() {
    let enabledPlugins = await this.getEnabledPlugins()
    if (!enabledPlugins) return

    this.ticketPluginEnabled = enabledPlugins.includes("ticket")
    this.conferencePluginEnabled = enabledPlugins.includes("conference")
    this.conversationPluginEnabled = enabledPlugins.includes("conversation")
    this.storagePluginEnabled = enabledPlugins.includes("storage")
    this.documentPluginEnabled = enabledPlugins.includes("document")
  },

  methods: {
    ...mapActions("incident", ["createAllResources", "getEnabledPlugins"]),
  },
}
</script>
