<template>
  <v-dialog v-model="showRun" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Run Workflow</span>
      </v-card-title>
      <span v-if="id">
        <v-card-text>
          <v-row dense>
            <v-col cols="12">
              <v-card>
                <v-list-item lines="two">
                  <v-list-item-title class="text-h6"> Workflow Details </v-list-item-title>
                  <v-list-item-subtitle
                    >{{ workflow.name }} - {{ workflow.resource_id }}</v-list-item-subtitle
                  >
                </v-list-item>
                <v-list class="bg-transparent">
                  <v-list-item>
                    <v-list-item-title>Status</v-list-item-title>
                    <v-list-item-subtitle class="text-right">
                      {{ status }}
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-for="artifact in artifacts" :key="artifact.id">
                    <v-list-item-title>Name</v-list-item-title>
                    <v-list-item-subtitle class="text-right">
                      {{ artifact.name }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="blue en-1" variant="text" @click="closeRun()"> Close </v-btn>
        </v-card-actions>
      </span>
      <span v-else>
        <v-card-text>
          <workflow-select v-model="workflow" />
          <span v-if="workflow.id">
            <workflow-parameters-input v-model="parameters" />
            <v-textarea
              v-model="run_reason"
              label="Run Reason"
              hint="Short note about why workflow is being run."
              clearable
            />
          </span>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="blue en-1" variant="text" @click="closeRun()"> Cancel </v-btn>
          <v-btn color="red en-1" variant="text" :loading="loading" @click="run()"> Run </v-btn>
        </v-card-actions>
      </span>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import WorkflowSelect from "@/workflow/WorkflowSelect.vue"
import WorkflowParametersInput from "@/workflow/WorkflowParametersInput.vue"
export default {
  name: "WorkflowRunModal",

  data() {
    return {}
  },

  components: {
    WorkflowSelect,
    WorkflowParametersInput,
  },
  computed: {
    ...mapFields("workflow", [
      "dialogs.showRun",
      "selected",
      "selectedInstance.case",
      "selectedInstance.incident",
      "selectedInstance.signal",
      "selectedInstance.id",
      "selectedInstance.status",
      "selectedInstance.loading",
      "selectedInstance.workflow",
      "selectedInstance.parameters",
      "selectedInstance.artifacts",
      "selectedInstance.run_reason",
    ]),
  },

  methods: {
    ...mapActions("workflow", ["closeRun", "run"]),
  },

  created() {
    this.$watch(
      (vm) => [vm.workflow],
      () => {
        // create a copy of the workflow params
        this.parameters = this.workflow.parameters
      }
    )
  },
}
</script>
