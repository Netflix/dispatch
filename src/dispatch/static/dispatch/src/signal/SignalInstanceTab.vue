<template>
  <v-data-table
    :headers="headers"
    :items="signalInstances"
    :items-per-page="25"
    :footer-props="{
      'items-per-page-options': [25, 50, 100],
    }"
  >
    <template #item.signal="{ value }">
      <signal-popover :value="value" />
    </template>
    <template #item.entities="{ value }">
      <v-row>
        <v-chip v-for="(entity, index) in value" :key="index" class="mr-2">
          {{ entity.entity_type.name }}
        </v-chip>
      </v-row>
    </template>
    <template #item.created_at="{ value }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <span v-bind="props">{{ formatRelativeDate(value) }}</span>
        </template>
        <span>{{ formatDate(value) }}</span>
      </v-tooltip>
    </template>
    <template #item.data-table-actions="{ item }">
      <v-btn icon variant="text" @click="showRun({ type: 'signal', data: item })">
        <v-icon>mdi-play-circle-outline</v-icon>
      </v-btn>
      <workflow-run-modal />
      <raw-signal-viewer :value="item" />
    </template>
  </v-data-table>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { formatRelativeDate, formatDate } from "@/filters"

import SignalPopover from "@/signal/SignalPopover.vue"
import RawSignalViewer from "@/signal/RawSignalViewer.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"

export default {
  name: "SignalInstanceTab",
  components: {
    SignalPopover,
    RawSignalViewer,
    WorkflowRunModal,
  },
  props: {
    inputSignalInstances: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      menu: false,
      workflowRunDialog: false,
      headers: [
        { title: "Signal", key: "signal", sortable: false },
        { title: "Entities", key: "entities", sortable: false },
        { title: "Created At", key: "created_at" },
        { title: "", key: "data-table-actions", sortable: false, align: "end" },
      ],
    }
  },
  setup() {
    return { formatRelativeDate, formatDate }
  },
  computed: {
    ...mapFields("case_management", ["selected.signal_instances"]),
    signalInstances() {
      if (this.inputSignalInstances.length) {
        return this.inputSignalInstances
      }
      return this.signal_instances
    },
  },
  methods: {
    ...mapActions("workflow", ["showRun"]),
  },
}
</script>
