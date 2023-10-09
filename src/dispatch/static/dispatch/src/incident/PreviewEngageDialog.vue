<template>
  <v-dialog v-model="showPreviewEngageDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="headline">Preview Engagement Filter</span>
      </v-card-title>
      <v-container grid-list-md>
        <v-layout wrap>
            <div class="text-body-2 ml-1 mt-2">Individuals</div>
            <v-divider class="mt-2" />
            <v-list style="max-height: 500px" class="overflow-y-auto">
              <template v-for="individual in individuals">
                <v-list-item :key="individual.id">
                  <v-list-item-content>
                    <incident-participant :participant="convertToParticipant(individual)" />
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-list>
            <div class="text-body-2 ml-1 mt-2">Teams</div>
            <v-divider class="mt-2" />
            <v-list style="max-height: 500px" class="overflow-y-auto">
              <template v-for="team in teams">
                <v-list-item :key="team.id">
                  <v-list-item-content>
                    <v-list-item-title>{{ team.name }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-list>
            <div class="text-body-2 ml-1 mt-2">Services</div>
            <v-divider class="mt-2" />
            <v-list style="max-height: 500px" class="overflow-y-auto">
              <template v-for="service in services">
                <v-list-item :key="service.id">
                  <v-list-item-content>
                    <v-list-item-title>{{ service.name }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-list>
            <div class="text-body-2 ml-1 mt-2">Notifications</div>
            <v-divider class="mt-2" />
            <v-list style="max-height: 500px" class="overflow-y-auto">
              <template v-for="notification in notifications">
                <v-list-item :key="notification.id">
                  <v-list-item-content>
                    <v-list-item-title>{{ notification.name }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </template>
            </v-list>
        </v-layout>
      </v-container>
        <v-card-actions>
        <v-spacer />
        <v-btn color="red en-1" text @click="closePreviewEngageDialog()"> Cancel </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
export default {
  name: "PreviewEngageDialog",
  data() {
    return {}
  },
  computed: {
    ...mapFields("incident", ["dialogs.showPreviewEngageDialog"]),
  },

  methods: {
    ...mapActions("incident", ["closePreviewEngageDialog"]),
  },
}
</script>
