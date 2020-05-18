<template>
  <div v-if="items.length">
    <edit-sheet />
    <v-divider></v-divider>
    <v-list>
      <v-list-group prepend-icon="star" no-action color="primary">
        <template v-slot:activator>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Incidents ({{ items.length }})</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
        <v-list-item
          v-for="item in items"
          :key="item.content.id"
          @click="showEditSheet(item.content)"
        >
          <v-list-item-content>
            <v-list-item-title v-text="item.content.name"></v-list-item-title>
            <v-list-item-subtitle>Name</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script>
import { mapActions } from "vuex"

import EditSheet from "@/incident/EditSheet.vue"
export default {
  name: "IncidentList",

  components: {
    EditSheet
  },

  props: {
    items: {
      default: null,
      type: Array
    }
  },

  methods: {
    ...mapActions("incident", ["showEditSheet"])
  }
}
</script>
