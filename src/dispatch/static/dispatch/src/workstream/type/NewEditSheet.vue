<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
      <template #prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Workstream Type</v-list-item-subtitle>
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
                    hint="A name for the workstream type."
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
                    hint="A description for the workstream type."
                    clearable
                    required
                  />
                </ValidationProvider>
              </v-flex>
              <v-flex xs12>
                <ValidationObserver disabled>
                  <template-select
                    :project="project"
                    label="Workstream Template"
                    v-model="document_template"
                    resource-type="dispatch-workstream-document-template"
                  />
                </ValidationObserver>
              </v-flex>
              <v-flex xs12>
                <ValidationObserver disabled>
                  <service-select
                    :project="project"
                    label="Oncall Service"
                    v-model="oncall_service"
                  />
                </ValidationObserver>
              </v-flex>
              <v-flex xs12>
                <v-checkbox
                  v-model="enabled"
                  label="Enabled"
                  hint="Indicates whether this workstream type is available or not."
                />
              </v-flex>
              <v-flex xs12>
                <plugin-metadata-input v-model="plugin_metadata" :project="project" />
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"

import ServiceSelect from "@/service/ServiceSelect.vue"
import TemplateSelect from "@/document/template/TemplateSelect.vue"

extend("required", {
  ...required,
  message: "This field is required",
})

export default {
  name: "WorkstreamTypeNewEditSheet",

  components: {
    ServiceSelect,
    TemplateSelect,
    ValidationObserver,
    ValidationProvider,
  },

  computed: {
    ...mapFields("workstream_type", [
      "dialogs.showCreateEdit",
      "selected.description",
      "selected.document_template",
      "selected.enabled",
      "selected.id",
      "selected.loading",
      "selected.name",
      "selected.oncall_service",
      "selected.project",
    ]),
    ...mapFields("route", ["query"]),
  },

  methods: {
    ...mapActions("workstream_type", ["save", "closeCreateEdit"]),
  },
  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
