<template>
  <div v-if="items.length">
    <new-edit-sheet />
    <v-divider />
    <v-list>
      <v-list-group prepend-icon="people" no-action color="info">
        <template v-slot:activator>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Organizations ({{ items.length }})</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
        <v-list-item
          v-for="item in items"
          :key="item.content.id"
          @click="createEditShow(item.content)"
        >
          <v-list-item-content>
            <v-list-item-title v-text="item.content.name" />
            <v-list-item-subtitle>Name</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script>
import { mapActions } from "vuex"

import NewEditSheet from "@/organization/NewEditSheet.vue"
export default {
  name: "OrganizationList",

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
    ...mapActions("organization", ["createEditShow"]),
  },
}
</script>
