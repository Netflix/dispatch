<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-card class="mx-auto ma-4" max-width="600" flat outlined :loading="loading">
      <v-card-text>
        <p class="display-1 text--primary">Report Incident</p>
        <p>
          If you suspect a incident and require help, please fill out the following to the best of
          your abilities.
        </p>
        <v-form>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <ValidationProvider name="Title" rules="required" immediate>
                  <v-textarea
                    v-model="title"
                    slot-scope="{ errors, valid }"
                    :error-messages="errors"
                    :success="valid"
                    label="Title"
                    hint="A brief explanatory title. You can change this later."
                    clearable
                    auto-grow
                    rows="2"
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
                    hint="A summary of what you know so far. It's all right if this is incomplete."
                    clearable
                    auto-grow
                    rows="3"
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <project-select v-model="project" />
              </v-flex>
              <v-flex xs12>
                <incident-type-select :project="project" v-model="incident_type" />
              </v-flex>
              <v-flex xs12>
                <incident-priority-select :project="project" v-model="incident_priority" />
              </v-flex>
              <v-flex xs12>
                <tag-filter-combobox :project="project" v-model="tags" label="Tags" />
              </v-flex>
              <v-flex xs12>
                <v-checkbox v-model="trackingOnly" label="Tracking Only">
                  <template v-slot:label>
                    <div>
                      Tracking Only
                      <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                          <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
                        </template>
                        Dispatch will only create a ticket for this incident. The status of the
                        incident will be closed and no collaboration resources will be created. No
                        further action from you will be needed.
                      </v-tooltip>
                    </div>
                  </template>
                </v-checkbox>
              </v-flex>
            </v-layout>
            <template>
              <v-btn
                color="info"
                depressed
                :loading="loading"
                :disabled="invalid || !validated"
                @click="report()"
              >
                Submit
                <template v-slot:loader>
                  <v-progress-linear indeterminate color="white" />
                </template>
              </v-btn>
            </template>
          </v-container>
        </v-form>
      </v-card-text>
    </v-card>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { required } from "vee-validate/dist/rules"
import IncidentTypeSelect from "@/incident_type/IncidentTypeSelect.vue"
import IncidentPrioritySelect from "@/incident_priority/IncidentPrioritySelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "ReportSubmissionCard",

  components: {
    ValidationProvider,
    ValidationObserver,
    IncidentTypeSelect,
    IncidentPrioritySelect,
    ProjectSelect,
    TagFilterCombobox,
  },
  data() {
    return {
      isSubmitted: false,
    }
  },
  computed: {
    ...mapFields("incident", [
      "selected.incident_priority",
      "selected.incident_type",
      "selected.commander",
      "selected.title",
      "selected.tags",
      "selected.description",
      "selected.conversation",
      "selected.conference",
      "selected.visibility",
      "selected.storage",
      "selected.documents",
      "selected.loading",
      "selected.ticket",
      "selected.project",
      "selected.trackingOnly",
      "selected.id",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("incident", ["report", "get", "resetSelected"]),
  },

  mounted() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }

    if (this.query.incident_type) {
      this.incident_type = { name: this.query.incident_type }
    }

    if (this.query.incident_priority) {
      this.incident_priority = { name: this.query.incident_priority }
    }
  },
}
</script>
