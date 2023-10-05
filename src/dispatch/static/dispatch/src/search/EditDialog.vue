<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer
      v-model="showCreateEdit"
      app
      clipped
      right
      width="500"
      :permanent="$vuetify.breakpoint.mdAndDown"
      class="overflow-y-auto"
    >
      <template #prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title class="title"> Edit </v-list-item-title>
            <v-list-item-subtitle>Search Filter</v-list-item-subtitle>
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
        <v-card flat>
          <v-card-text>
            <v-container grid-list-md>
              <v-layout wrap>
                <v-flex xs12>
                  <ValidationProvider name="Name" rules="required" immediate>
                    <v-text-field
                      v-model="name"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="Name"
                      hint="Name of type."
                      clearable
                      required
                    />
                  </ValidationProvider>
                </v-flex>
                <v-flex xs12>
                  <ValidationProvider name="Description" rules="required" immediate>
                    <v-textarea
                      v-model="description"
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      label="Description"
                      hint="Description of type."
                      clearable
                      required
                    />
                  </ValidationProvider>
                </v-flex>
              </v-layout>
              <div class="text-body-2 ml-1 mt-2">Individuals</div>
              <v-divider class="mt-2" />
              <v-list style="max-height: 500px" class="overflow-y-auto">
                <template v-for="individual in individuals">
                  <v-list-item :key="individual.id">
                    <v-list-item-content>
                      <v-list-item-title>{{ individual.name }}</v-list-item-title>
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
            </v-container>
          </v-card-text>
        </v-card>
      </template>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationProvider, ValidationObserver, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "SearchEditDialog",

  components: {
    ValidationProvider,
    ValidationObserver,
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
  },
}
</script>
