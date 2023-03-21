<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn icon v-on="on">
        <v-icon>add</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Create Workflow</span>
        <v-spacer></v-spacer>
      </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-step :complete="step > 1" step="1" editable> Filter </v-stepper-step>
          <v-divider />
          <v-stepper-step step="2" editable> Save </v-stepper-step>
        </v-stepper-header>

        <v-stepper-items>
          <v-stepper-content step="1">
            <v-card>
              <v-card-text>
                Define the entity types that will be used to paramterize the workflow.
                <v-flex xs12>
                  <plugin-instance-combobox
                    v-model="plugin_instance"
                    type="workflow"
                    :project="project"
                    label="Plugin"
                  />
                </v-flex>
                <v-flex xs12>
                  <ValidationProvider name="resourceId" rules="required" immediate>
                    <v-text-field
                      v-model="resource_id"
                      slot-scope="{ errors, valid }"
                      label="Resource Id"
                      :error-messages="errors"
                      :success="valid"
                      required
                      hint="External resource id that refers to this workflow."
                    />
                  </ValidationProvider>
                </v-flex>
                <v-flex xs12>
                  <workflow-parameters-entity-input v-model="parameters" />
                </v-flex>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>

          <v-stepper-content step="2">
            <ValidationObserver disabled v-slot="{ invalid, validated }">
              <v-card>
                <v-card-text>
                  Provide a name and description for your workflow.
                  <ValidationProvider name="Name" rules="required" immediate>
                    <v-text-field
                      v-model="name"
                      label="Name"
                      hint="A name for your saved search."
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      clearable
                      required
                    />
                  </ValidationProvider>
                  <ValidationProvider name="Description" rules="required" immediate>
                    <v-textarea
                      v-model="description"
                      label="Description"
                      hint="A short description."
                      slot-scope="{ errors, valid }"
                      :error-messages="errors"
                      :success="valid"
                      clearable
                      auto-grow
                    />
                  </ValidationProvider>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="closeCreateEditDialog()" text> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveWorkflow()"
                    :loading="loading"
                    :disabled="invalid || !validated"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </ValidationObserver>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { ValidationObserver, ValidationProvider, extend } from "vee-validate"
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { required } from "vee-validate/dist/rules"
import EntityTypeSelect from "@/entity_type/EntityTypeSelect.vue"
import PluginInstanceCombobox from "@/plugin/PluginInstanceCombobox.vue"
import WorkflowParametersEntityInput from "@/workflow/WorkflowParametersEntityInput.vue"

extend("required", {
  ...required,
  message: "This field is required",
})
export default {
  name: "WorkflowCreateDialog",
  props: {
    value: {
      type: Object,
      default: null,
    },
    signalDefinition: {
      type: Object,
      required: false,
    },
  },
  data() {
    return {
      step: 1,
    }
  },
  components: {
    EntityTypeSelect,
    PluginInstanceCombobox,
    ValidationObserver,
    ValidationProvider,
    WorkflowParametersEntityInput,
  },
  computed: {
    ...mapFields("workflow", [
      "selected.name",
      "selected.description",
      "selected.enabled",
      "selected.resource_id",
      "selected.parameters",
      "selected.id",
      "selected.plugin_instance",
      "selected.project",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
  },
  methods: {
    ...mapActions("workflow", ["closeCreateEditDialog", "save"]),
    saveWorkflow() {
      // reset local data
      this.save().then((workflow) => {
        this.$emit("input", workflow)
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
