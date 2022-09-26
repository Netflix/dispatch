<template>
  <v-dialog v-model="showRun" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="headline">Run Workflow</span>
      </v-card-title>
      <v-card-text>
        <workflow-select v-model="selected" />
        <workflow-parameters-input v-model="parameters" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" text @click="closeRun()"> Cancel </v-btn>
        <v-btn color="red en-1" text @click="run(value)"> Run </v-btn>
      </v-card-actions>
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
    ...mapFields("workflow", ["dialogs.showRun", "selected", "selected.parameters"]),
  },

  methods: {
    ...mapActions("workflow", ["closeRun", "run"]),
  },
}
</script>
