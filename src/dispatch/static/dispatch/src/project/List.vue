<template>
  <div v-if="items.length">
    <new-edit-sheet />
    <v-divider />
    <v-list>
      <v-list-group prepend-icon="mdi-account-multiple" color="info">
        <template #activator="{ props }">
          <v-list-item v-bind="props">
            <v-list-item-title>Projects ({{ items.length }})</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item
          v-for="item in items"
          :key="item.content.id"
          @click="createEditShow(item.content)"
        >
          <v-list-item-title>{{ item.content.name }}</v-list-item-title>
          <v-list-item-subtitle>Name</v-list-item-subtitle>
        </v-list-item>
      </v-list-group>
    </v-list>
  </div>
</template>
<script>
import { mapActions } from "vuex"

import NewEditSheet from "@/project/NewEditSheet.vue"
export default {
  name: "ProjectList",

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
    ...mapActions("project", ["createEditShow"]),
  },
}
</script>
