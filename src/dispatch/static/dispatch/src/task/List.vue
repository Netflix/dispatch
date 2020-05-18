<template>
  <div v-if="items.length">
    <new-edit-sheet />
    <v-divider></v-divider>
    <v-list>
      <v-list-group prepend-icon="playlist_add_check" no-action color="primary">
        <template v-slot:activator>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Tasks ({{ items.length }})</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
        <v-list-item
          v-for="item in items"
          :key="item.content.id"
          @click="showNewEditSheet(item.content)"
        >
          <v-list-item-content>
            <v-list-item-title v-text="item.content.description"></v-list-item-title>
            <v-list-item-subtitle>Description</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script>
import { mapActions } from "vuex"

import NewEditSheet from "@/task/NewEditSheet.vue"
export default {
  name: "TaskList",

  components: {
    NewEditSheet
  },

  props: {
    items: {
      default: null,
      type: Array
    }
  },

  methods: {
    ...mapActions("task", ["showNewEditSheet"])
  }
}
</script>
