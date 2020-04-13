<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showNewSheet" app clipped right width="800">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title class="title">New</v-list-item-title>
          </v-list-item-content>
          <v-btn
            icon
            color="primary"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon color="secondary" @click="closeNewSheet">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-tabs v-model="tab">
        <v-tab key="details">Details</v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <incident-details-tab />
      </v-tabs-items>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver } from "vee-validate"

import IncidentDetailsTab from "@/incident/DetailsTab.vue"

export default {
  name: "IncidentNewSheet",

  components: {
    ValidationObserver,
    IncidentDetailsTab
  },

  data() {
    return {
      tab: null
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.reported_at",
      "selected.loading",
      "dialogs.showNewSheet"
    ])
  },

  methods: {
    ...mapActions("incident", ["save", "closeNewSheet"])
  }
}
</script>
