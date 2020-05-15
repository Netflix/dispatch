<template>
  <div v-if="items.length">
    <new-edit-sheet />
    <v-divider></v-divider>
    <v-list>
      <v-list-group prepend-icon="room_service" no-action color="primary">
        <template v-slot:activator>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Services ({{ items.length }})</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
        <v-list-item
          v-for="item in items"
          :key="item.content.id"
          @click="createEditShow(item.content)"
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

import NewEditSheet from "@/service/NewEditSheet.vue"
export default {
  name: "ServiceList",

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
    ...mapActions("service", ["createEditShow"])
  }
}
</script>
