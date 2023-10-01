<template>
  <v-dialog v-model="showCreateEdit" persistent max-width="800px">
    <template #activator="{ props }">
      <v-btn icon variant="text" v-bind="props">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Create Workflow</span>
        <v-spacer />
      </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-item :complete="step > 1" :value="1" editable> Filter </v-stepper-item>
          <v-divider />
          <v-stepper-item :value="2" editable> Save </v-stepper-item>
        </v-stepper-header>

        <v-stepper-window>
          <v-stepper-window-item :value="1">
            <v-card>
              <v-card-text>
                Define the entity types that will be used to paramterize the workflow.
                <v-col cols="12">
                  <plugin-instance-combobox
                    v-model="plugin_instance"
                    type="workflow"
                    :project="project"
                    label="Plugin"
                  />
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="resource_id"
                    label="Resource Id"
                    required
                    hint="External resource id that refers to this workflow."
                    name="resourceId"
                    :rules="[rules.required]"
                  />
                </v-col>
                <v-col cols="12">
                  <workflow-parameters-entity-input v-model="parameters" />
                </v-col>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateEditDialog()" variant="text"> Cancel </v-btn>
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-window-item>

          <v-stepper-window-item :value="2">
            <v-form @submit.prevent v-slot="{ isValid }">
              <v-card>
                <v-card-text>
                  Provide a name and description for your workflow.
                  <v-text-field
                    v-model="name"
                    label="Name"
                    hint="A name for your saved search."
                    clearable
                    required
                    name="Name"
                    :rules="[rules.required]"
                  />
                  <v-textarea
                    v-model="description"
                    label="Description"
                    hint="A short description."
                    clearable
                    auto-grow
                    name="Description"
                    :rules="[rules.required]"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="closeCreateEditDialog()" variant="text"> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveWorkflow()"
                    :loading="loading"
                    :disabled="!isValid.value"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-stepper-window-item>
        </v-stepper-window>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import PluginInstanceCombobox from "@/plugin/PluginInstanceCombobox.vue"
import WorkflowParametersEntityInput from "@/workflow/WorkflowParametersEntityInput.vue"
export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "WorkflowCreateDialog",
  data() {
    return {
      step: 1,
    }
  },
  components: {
    PluginInstanceCombobox,
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
  },
  methods: {
    ...mapActions("workflow", ["closeCreateEditDialog", "save"]),
    saveWorkflow() {
      // reset local data
      this.save().then((workflow) => {
        this.$emit("save", workflow)
      })
    },
  },
  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
