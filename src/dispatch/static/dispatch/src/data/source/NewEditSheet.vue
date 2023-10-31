<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="600">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Source</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-tabs v-model="activeTab">
        <v-tab> Basic Info </v-tab>
        <v-tab> Queries </v-tab>
        <v-tab> Incidents </v-tab>
        <v-tab> Links </v-tab>
      </v-tabs>
      <v-window v-model="activeTab">
        <v-window-item>
          <edit-basic-info-tab />
        </v-window-item>
        <v-window-item>
          <edit-queries-tab v-model="queries" />
        </v-window-item>
        <v-window-item>
          <edit-incidents-tab v-model="incidents" />
        </v-window-item>
        <v-window-item>
          <edit-links-tab />
        </v-window-item>
      </v-window>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import EditBasicInfoTab from "@/data/source/EditBasicInfoTab.vue"
import EditIncidentsTab from "@/data/source/EditIncidentsTab.vue"
import EditQueriesTab from "@/data/source/EditQueriesTab.vue"
import EditLinksTab from "@/data/source/EditLinksTab.vue"

export default {
  name: "SourceNewEditSheet",

  components: {
    EditBasicInfoTab,
    EditIncidentsTab,
    EditQueriesTab,
    EditLinksTab,
  },

  data: () => ({
    activeTab: 0,
  }),

  computed: {
    ...mapFields("source", [
      "selected.id",
      "selected.loading",
      "selected.incidents",
      "selected.queries",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("source", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("source/save").then(function (data) {
        self.$emit("new-source-created", data)
      })
    },
  },
}
</script>
