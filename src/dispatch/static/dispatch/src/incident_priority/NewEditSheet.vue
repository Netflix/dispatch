<template>
  <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="id" class="title">Edit</v-list-item-title>
          <v-list-item-title v-else class="title">New</v-list-item-title>
          <v-list-item-subtitle>Incident Priority</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
    <ValidationObserver>
      <v-card slot-scope="{ invalid, validated }" flat>
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
                    hint="a name for your incident priority."
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
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your incident priority."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="View Order" rules="required" immediate>
                  <v-text-field
                    v-model="view_order"
                    slot-scope="{ errors, valid }"
                    label="View Order"
                    :error-messages="errors"
                    :success="valid"
                    type="number"
                    hint="Enter an value indicating where you want this priority to be in a list (lowest are first)."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Status Reminder" rules="required" immediate>
                  <v-text-field
                    v-model="status_reminder"
                    slot-scope="{ errors, valid }"
                    label="Status Reminder"
                    :error-messages="errors"
                    :success="valid"
                    type="number"
                    hint="Number of hours to send a status report reminder to the incident commander."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex>
                <v-switch
                  v-model="page_commander"
                  label="Page Commander"
                  hint="Would you like Dispatch to page the incident commander on incident creation?"
                ></v-switch>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn color="secondary" @click="closeCreateEdit()">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >Save</v-btn>
        </v-card-actions>
      </v-card>
    </ValidationObserver>
  </v-navigation-drawer>
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
  name: "IncidentPriorityNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider
  },

  data() {
    return {}
  },

  computed: {
    ...mapFields("incident_priority", [
      "dialogs.showCreateEdit",
      "selected.description",
      "selected.id",
      "selected.loading",
      "selected.name",
      "selected.view_order",
      "selected.page_commander",
      "selected.status_reminder"
    ])
  },

  methods: {
    ...mapActions("incident_priority", ["save", "closeCreateEdit"])
  }
}
</script>
