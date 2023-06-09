<template>
  <v-data-table
    :headers="headers"
    :items="signalInstances"
    :items-per-page="25"
    :footer-props="{
      'items-per-page-options': [25, 50, 100],
    }"
  >
    <template v-slot:item.signal="{ item }">
      <signal-popover v-model="item.signal" />
    </template>
    <template v-slot:item.entities="{ item }">
      <v-row>
        <v-chip v-for="(entity, index) in item.entities" :key="index" class="mr-2">
          {{ entity.entity_type.name }}
        </v-chip>
      </v-row>
    </template>
    <template v-slot:item.created_at="{ item }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <span v-bind="attrs" v-on="on">{{ item.created_at | formatRelativeDate }}</span>
        </template>
        <span>{{ item.created_at | formatDate }}</span>
      </v-tooltip>
    </template>
    <template v-slot:item.data-table-actions="{ item }">
      <v-btn icon @click="showRun({ type: 'signal', data: item })">
        <v-icon>mdi-play-circle-outline</v-icon>
      </v-btn>
      <workflow-run-modal />
      <raw-signal-viewer v-model="item.raw" />
    </template>
  </v-data-table>
</template>

<script lang="ts">
import CaseApi from "@/case/api"
import SignalPopover from "@/signal/SignalPopover.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"

export default {
  name: "SignalInstanceCardViewer",
  components: {
    SignalPopover,
    RawSignalViewer,
    WorkflowRunModal,
  },
  props: {
    caseId: {
      type: Number,
    },
  },
  data() {
    return {
      menu: false,
      workflowRunDialog: false,
      signalInstances: [],
      headers: [
        { text: "Signal", value: "signal", sortable: false },
        { text: "Entities", value: "entities", sortable: false },
        { text: "Created At", value: "created_at" },
        { text: "", value: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  watch: {
    caseId(newCaseId) {
      this.fetchSignalInstances(newCaseId)
    },
  },
  methods: {
    async fetchSignalInstances(caseId: Number) {
      const signalPromise = CaseApi.getAllSignalInstances(caseId).then((response) => response.data)
      const signalResponse = await signalPromise
      if (Array.isArray(signalResponse.instances) && signalResponse.instances.length) {
        this.signalInstances = signalResponse.instances.flat()
      } else {
        console.log("Response data is not in the expected format")
      }
    },
  },
  created() {
    this.fetchSignalInstances(this.caseId)
  },
}
</script>
