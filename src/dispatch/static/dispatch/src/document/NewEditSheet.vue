<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Document</v-list-item-subtitle>
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
                    hint="A name for your document."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="description" immediate>
                  <v-textarea
                    v-model="description"
                    slot-scope="{ errors, valid }"
                    label="Description"
                    :error-messages="errors"
                    :success="valid"
                    hint="A description for your document."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Document Weblink" rules="required" immediate>
                  <v-text-field
                    v-model="weblink"
                    slot-scope="{ errors, valid }"
                    label="Weblink"
                    :error-messages="errors"
                    :success="valid"
                    hint="A weblink for the document."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Resource Id" immediate>
                  <v-text-field
                    v-model="resource_id"
                    slot-scope="{ errors, valid }"
                    label="External Id"
                    :error-messages="errors"
                    :success="valid"
                    hint="External identifier for document. Used for API integration (e.g. Google doc file id). Typically is the unique id in the weblink."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Resource Type" immediate>
                  <v-text-field
                    v-model="resource_type"
                    slot-scope="{ errors, valid }"
                    label="Type"
                    :error-messages="errors"
                    :success="valid"
                    hint="The type of resource document."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2"
                  >Engagement
                  <v-tooltip max-width="250px" bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                    </template>
                    This document will be automatically suggessted for any incident matching the
                    following filters.
                  </v-tooltip>
                </span>
              </v-flex>
              <v-flex xs12>
                <term-combobox :project="project" v-model="terms" />
              </v-flex>
              <v-flex xs12>
                <incident-priority-multi-select :project="project" v-model="incident_priorities" />
              </v-flex>
              <v-flex>
                <incident-type-multi-select :project="project" v-model="incident_types" />
              </v-flex>
              <v-flex xs12>
                <span class="subtitle-2">Evergreen</span>
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="evergreen"
                  hint="Enabling evergreen will send periodic reminders to the owner to update this document."
                  label="Enabled"
                />
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Owner" immediate>
                  <v-text-field
                    v-model="evergreen_owner"
                    slot-scope="{ errors, valid }"
                    label="Owner"
                    :error-messages="errors"
                    :success="valid"
                    hint="Owner of this document."
                    clearable
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationProvider name="Reminder Interval" immediate>
                  <v-text-field
                    v-model="evergreen_reminder_interval"
                    slot-scope="{ errors, valid }"
                    label="Reminder Interval"
                    :error-messages="errors"
                    :success="valid"
                    type="number"
                    hint="Number of days that should elapse between reminders sent to the document owner."
                    placeholder="90"
                    clearable
                    min="1"
                  />
                </ValidationProvider>
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
import IncidentPriorityMultiSelect from "@/incident_priority/IncidentPriorityMultiSelect.vue"
import IncidentTypeMultiSelect from "@/incident_type/IncidentTypeMultiSelect.vue"
import TermCombobox from "@/term/TermCombobox.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "DocumentNewEditSheet",

  components: {
    ValidationObserver,
    ValidationProvider,
    IncidentPriorityMultiSelect,
    IncidentTypeMultiSelect,
    TermCombobox,
  },

  computed: {
    ...mapFields("document", [
      "selected.name",
      "selected.description",
      "selected.terms",
      "selected.resource_type",
      "selected.weblink",
      "selected.resource_id",
      "selected.incident_priorities",
      "selected.incident_types",
      "selected.evergreen_owner",
      "selected.evergreen",
      "selected.evergreen_reminder_interval",
      "selected.project",
      "selected.id",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("document", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("document/save").then(function (data) {
        self.$emit("new-document-created", data)
      })
    },
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
