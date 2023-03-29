<template>
  <v-dialog v-model="showRun" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="headline">Run Workflow</span>
      </v-card-title>
      <span v-if="id">
        <v-card-text>
          <v-row dense>
            <v-col cols="12">
              <v-card outlined elevation="0">
                <v-list-item two-line>
                  <v-list-item-content>
                    <v-list-item-title class="text-h6"> Workflow Details </v-list-item-title>
                    <v-list-item-subtitle
                      >{{ workflow.name }} - {{ workflow.resource_id }}</v-list-item-subtitle
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list class="transparent">
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
          <v-btn color="blue en-1" text @click="closeRun()"> Close </v-btn>
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
          <v-btn color="blue en-1" text @click="closeRun()"> Cancel </v-btn>
          <v-btn color="red en-1" text :loading="loading" @click="run()"> Run </v-btn>
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
  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

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
