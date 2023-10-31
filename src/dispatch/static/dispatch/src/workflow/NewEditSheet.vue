<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Workflow</v-list-item-subtitle>

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
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-card>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <span class="text-subtitle-2">Details</span>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="name"
                  label="Name"
                  hint="A name for your workflow."
                  required
                  name="name"
                  :rules="[rules.required]"
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
                <v-textarea
                  v-model="description"
                  label="Description"
                  hint="The workflow's description."
                  clearable
                  required
                  name="description"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <plugin-instance-combobox
                  v-model="plugin_instance"
                  type="workflow"
                  :project="project"
                  label="Plugin"
                />
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="enabled"
                  hint="Disabled workflows will not be made available for selection during incidents."
                  label="Enabled"
                />
              </v-col>
              <v-col cols="12">
                <workflow-parameters-input v-model="parameters" />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import PluginInstanceCombobox from "@/plugin/PluginInstanceCombobox.vue"
import WorkflowParametersInput from "@/workflow/WorkflowParametersInput.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "WorkflowNewEditSheet",

  components: {
    PluginInstanceCombobox,
    WorkflowParametersInput,
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
    ...mapActions("workflow", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
