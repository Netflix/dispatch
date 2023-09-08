<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer
      v-model="showNewSheet"
      app
      clipped
      location="right"
      width="800"
      :permanent="$vuetify.display.mdAndDown"
    >
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title class="text-h6"> New </v-list-item-title>

          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!isValid.value || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeNewSheet">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-tabs color="primary" v-model="tab">
        <v-tab key="details"> Details </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <incident-details-tab />
      </v-tabs-items>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import IncidentDetailsTab from "@/incident/DetailsTab.vue"

export default {
  name: "IncidentNewSheet",

  components: {
    IncidentDetailsTab,
  },

  data() {
    return {
      tab: null,
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.reported_at",
      "selected.loading",
      "dialogs.showNewSheet",
    ]),
  },

  methods: {
    ...mapActions("incident", ["save", "closeNewSheet"]),
  },
}
</script>
