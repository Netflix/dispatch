<template>
  <div v-if="items.length">
    <new-edit-sheet />
    <v-divider />
    <v-list>
      <v-list-group prepend-icon="mdi-playlist-check" color="info">
        <template #activator="{ props }">
          <v-list-item v-bind="props">
            <v-list-item-title>Workflows ({{ items.length }})</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item
          v-for="item in items"
          :key="item.content.id"
          @click="showNewEditSheet(item.content)"
        >
          <v-list-item-title>{{ item.content.description }}</v-list-item-title>
          <v-list-item-subtitle>Description</v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script>
import { mapActions } from "vuex"

import NewEditSheet from "@/workflow/NewEditSheet.vue"
export default {
  name: "WorkflowList",

  components: {
    NewEditSheet,
  },

  props: {
    items: {
      default: null,
      type: Array,
    },
  },

  methods: {
    ...mapActions("workflow", ["showNewEditSheet"]),
  },
}
</script>
