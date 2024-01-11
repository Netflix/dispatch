<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer
      v-model="showCreateEdit"
      location="right"
      width="500"
      :permanent="$vuetify.display.mdAndDown"
    >
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title class="text-h6"> Edit </v-list-item-title>
          <v-list-item-subtitle>Search Filter</v-list-item-subtitle>

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
      <v-container>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="name"
              label="Name"
              name="Name"
              hint="Name of type."
              clearable
              required
              :rules="[rules.required]"
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              v-model="description"
              label="Description"
              name="Description"
              hint="Description of type."
              clearable
              required
              :rules="[rules.required]"
            />
          </v-col>
        </v-row>
        <div class="text-body-2 ml-1 mt-2">Individuals</div>
        <v-divider class="mt-2" />
        <v-list style="max-height: 500px">
          <v-list-item v-for="individual in individuals" :key="individual.id">
            <incident-participant :participant="convertToParticipant(individual)" />
          </v-list-item>
        </v-list>
        <div class="text-body-2 ml-1 mt-2">Teams</div>
        <v-divider class="mt-2" />
        <v-list style="max-height: 500px">
          <v-list-item v-for="team in teams" :key="team.id">
            <v-list-item-title>{{ team.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
        <div class="text-body-2 ml-1 mt-2">Services</div>
        <v-divider class="mt-2" />
        <v-list style="max-height: 500px">
          <v-list-item v-for="service in services" :key="service.id">
            <v-list-item-title>{{ service.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
        <div class="text-body-2 ml-1 mt-2">Notifications</div>
        <v-divider class="mt-2" />
        <v-list style="max-height: 500px">
          <v-list-item v-for="notification in notifications" :key="notification.id">
            <v-list-item-title>{{ notification.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-container>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import IncidentParticipant from "@/incident/Participant.vue"
import { required } from "@/util/form"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "SearchEditDialog",

  components: {
    IncidentParticipant,
  },

  computed: {
    ...mapFields("search", [
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.loading",
      "selected.individuals",
      "selected.teams",
      "selected.services",
      "selected.notifications",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("search", ["closeCreateEdit", "save"]),
    convertToParticipant(individual) {
      return {
        individual: {
          name: individual.name,
          email: individual.email,
        },
      }
    },
  },
}
</script>
