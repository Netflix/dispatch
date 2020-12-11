<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showNewSheet" app clipped right width="800">
      <template v-slot:prepend>
        <v-card elevation="0">
          <v-toolbar color="primary" class="elevation-1">
            <v-toolbar-title>Create Incident</v-toolbar-title>

            <v-spacer></v-spacer>

            <v-btn
              icon
              color="info"
              :loading="loading"
              :disabled="invalid || !validated"
              @click="save()"
            >
              <v-icon>save</v-icon>
            </v-btn>
            <v-btn icon color="secondary" @click="closeNewSheet()">
              <v-icon>close</v-icon>
            </v-btn>

            <template v-slot:extension>
              <v-tabs v-model="tab" align-with-title color="gray0" e>
                <v-tab key="details">Details</v-tab>
              </v-tabs>
            </template>
          </v-toolbar>

          <v-tabs-items v-model="tab">
            <incident-details-tab />
          </v-tabs-items>
        </v-card>
      </template>
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
