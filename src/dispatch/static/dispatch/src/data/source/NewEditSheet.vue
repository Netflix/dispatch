<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="600">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Source</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn
            icon
            color="info"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon color="secondary" @click="closeCreateEdit">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-tabs>
        <v-tab> Basic Info </v-tab>
        <v-tab> Queries </v-tab>
        <v-tab> Incidents </v-tab>
        <v-tab> Links </v-tab>
        <v-tab-item>
          <edit-basic-info-tab />
        </v-tab-item>
        <v-tab-item>
          <edit-queries-tab v-model="queries" />
        </v-tab-item>
        <v-tab-item>
          <edit-incidents-tab v-model="incidents" />
        </v-tab-item>
        <v-tab-item>
          <edit-links-tab />
        </v-tab-item>
      </v-tabs>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver } from "vee-validate"

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
    ValidationObserver,
  },

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
