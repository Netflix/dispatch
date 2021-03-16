<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title">Edit</v-list-item-title>
            <v-list-item-title v-else class="title">New</v-list-item-title>
            <v-list-item-subtitle>Incident Cost Type</v-list-item-subtitle>
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
          <v-btn icon color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-card flat>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <span class="subtitle-2">Details</span>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Name" rules="required" immediate>
                  <v-text-field
                    v-model="name"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Name"
                    hint="A name for the incident cost type."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Description" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for the incident cost type."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <!-- TODO(mvilanova): Add section for cost type details -->
              <v-flex xs12>
                <v-checkbox
                  v-model="default_incident_cost_type"
                  label="Default"
                  hint="Check this if this incident cost type should be the default."
                />
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="editable"
                  label="Editable"
                  hint="Whether this cost type can be edited or not."
                  value
                  disabled
                />
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"

extend("required", {
  ...required,
  message: "This field is required"
})

export default {
  name: "IncidentCostTypeNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider
  },

  computed: {
    ...mapFields("incident_cost_type", [
      "selected.name",
      "selected.description",
      "selected.details",
      "selected.editable",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit"
    ]),
    ...mapFields("incident_cost_type", {
      default_incident_cost_type: "selected.default"
    })
  },

  methods: {
    ...mapActions("incident_cost_type", ["save", "closeCreateEdit"])
  }
}
</script>
