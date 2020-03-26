<template>
  <v-navigation-drawer v-model="showCreateEdit" app clipped right width="800">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="id" class="title">Edit - {{ name }}</v-list-item-title>
          <v-list-item-title v-else class="title">New</v-list-item-title>
          <v-list-item-subtitle>Created: {{ created_at | formatDate }}</v-list-item-subtitle>
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
                <ValidationProvider name="Title" rules="required" immediate>
                  <v-text-field
                    v-model="title"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Title"
                    hint="Title of incident."
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
                    hint="Description of incident."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <v-select
                  v-model="status"
                  label="Status"
                  :items="statuses"
                  hint="The incident's current status"
                  clearable
                />
              </v-flex>
              <v-flex xs12>
                <v-select
                  v-model="visibility"
                  label="Visibility"
                  :items="visibilities"
                  hint="The incident's current's visibilty"
                  clearable
                />
              </v-flex>
              <v-flex xs12>
                <incident-type-select v-model="incident_type" />
              </v-flex>
              <v-flex xs12>
                <incident-priority-select v-model="incident_priority" />
              </v-flex>
              <v-flex xs12>
                <term-combobox v-model="terms" />
              </v-flex>
              <v-flex xs12>
                <tag-combobox v-model="tags" />
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2">People</span>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Commander" rules="required" immediate>
                  <individual-select
                    v-model="commander"
                    slot-scope="{ errors, valid }"
                    label="Commander"
                    :error-messages="errors"
                    :success="valid"
                    hint="The incident's current commander"
                    clearable
                    required
                  ></individual-select>
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Reporter" rules="required" immediate>
                  <individual-select
                    v-model="reporter"
                    slot-scope="{ errors, valid }"
                    label="Reporter"
                    :error-messages="errors"
                    :success="valid"
                    hint="The incident's current reporter"
                    clearable
                    required
                  ></individual-select>
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2">Reported At</span>
              </v-flex>
              <v-flex xs12>
                <v-row>
                  <v-col cols="6">
                    <date-picker-menu v-model="reported_at"></date-picker-menu>
                  </v-col>
                  <v-col cols="6">
                    <time-picker-menu v-model="reported_at"></time-picker-menu>
                  </v-col>
                </v-row>
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2">Stable At</span>
              </v-flex>
              <v-flex xs12>
                <v-row>
                  <v-col cols="6">
                    <date-picker-menu v-model="stable_at"></date-picker-menu>
                  </v-col>
                  <v-col cols="6">
                    <time-picker-menu v-model="stable_at"></time-picker-menu>
                  </v-col>
                </v-row>
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
import { ValidationObserver, ValidationProvider } from "vee-validate"
import IncidentPrioritySelect from "@/incident_priority/IncidentPrioritySelect.vue"
import IncidentTypeSelect from "@/incident_type/IncidentTypeSelect.vue"
import IndividualSelect from "@/individual/IndividualSelect.vue"
import DatePickerMenu from "@/components/DatePickerMenu.vue"
import TimePickerMenu from "@/components/TimePickerMenu.vue"
import TermCombobox from "@/term/TermCombobox.vue"
import TagCombobox from "@/tag/TagCombobox.vue"

export default {
  name: "IncidentNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    IncidentPrioritySelect,
    IncidentTypeSelect,
    IndividualSelect,
    TermCombobox,
    TagCombobox,
    TimePickerMenu,
    DatePickerMenu
  },

  data() {
    return {
      statuses: ["Active", "Stable", "Closed"],
      visibilities: ["Open", "Restricted"]
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.id",
      "selected.name",
      "selected.title",
      "selected.description",
      "selected.commander",
      "selected.reporter",
      "selected.created_at",
      "selected.stable_at",
      "selected.reported_at",
      "selected.status",
      "selected.terms",
      "selected.tags",
      "selected.incident_priority",
      "selected.incident_type",
      "selected.visibility",
      "selected.loading",
      "dialogs.showCreateEdit"
    ])
  },

  methods: {
    ...mapActions("incident", ["save", "closeCreateEdit"])
  }
}
</script>
