<template>
  <v-list>
    <v-list-item v-if="ticket" :href="ticket.weblink" target="_blank">
      <v-list-item-title>Ticket</v-list-item-title>
      <v-list-item-subtitle>{{ ticket.description }}</v-list-item-subtitle>

      <template #append>
        <v-icon>mdi-open-in-new</v-icon>
      </template>
    </v-list-item>
    <v-divider />
    <v-list-item v-if="conversation" :href="conversation.weblink" target="_blank">
      <v-list-item-title>Conversation</v-list-item-title>
      <v-list-item-subtitle>{{ conversation.description }}</v-list-item-subtitle>

      <template #append>
        <v-icon>mdi-open-in-new</v-icon>
      </template>
    </v-list-item>
    <v-divider />
    <span v-for="group in groups" :key="group.resource_id">
      <v-list-item :href="group.weblink" target="_blank">
        <v-list-item-title>{{ deslug(group.resource_type) }}</v-list-item-title>
        <v-list-item-subtitle>{{ group.description }}</v-list-item-subtitle>

        <template #append>
          <v-icon>mdi-open-in-new</v-icon>
        </template>
      </v-list-item>
      <v-divider />
    </span>
    <v-divider />
    <v-list-item v-if="storage" :href="storage.weblink" target="_blank">
      <v-list-item-title>Storage</v-list-item-title>
      <v-list-item-subtitle>{{ storage.description }}</v-list-item-subtitle>

      <template #append>
        <v-icon>mdi-open-in-new</v-icon>
      </template>
    </v-list-item>
    <v-divider />
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
  </v-list>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { deslug } from "@/filters"

export default {
  name: "CaseResourcesTab",

  setup() {
    return { deslug }
  },

  computed: {
    ...mapFields("case_management", [
      "selected.documents",
      "selected.groups",
      "selected.storage",
      "selected.ticket",
      "selected.conversation",
    ]),
  },
}
</script>
