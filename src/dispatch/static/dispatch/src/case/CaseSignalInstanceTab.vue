<template>
  <v-data-table
    density="compact"
    :headers="headers"
    :loading="internalLoading"
    :items="signalInstances"
    :items-per-page="25"
    :footer-props="{
      'items-per-page-options': [25, 50, 100],
    }"
  >
    <template #item.signal="{ value }">
      <signal-popover :value="value" />
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
import { ref, toRefs, watch } from "vue"
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
    modelValue: {
      type: Array,
      default: () => [],
      required: true,
    },
    loading: {
      type: Boolean,
      default: false,
      required: true,
    },
  },
  setup(props) {
    const { modelValue, loading } = toRefs(props)
    const signalInstances = ref(props.modelValue)
    const internalLoading = ref(props.loading)

    watch(modelValue, (newValue) => {
      signalInstances.value = newValue
    })

    watch(loading, (newValue) => {
      internalLoading.value = newValue
    })

    const headers = ref([
      { title: "Signal", key: "signal", sortable: false },
      { title: "Created At", key: "created_at" },
      { title: "", key: "data-table-actions", sortable: false, align: "end" },
    ])

    function showRun(payload) {
      store.dispatch("workflow/showRun", payload)
    }

    return { formatRelativeDate, formatDate, signalInstances, headers, showRun, internalLoading }
  },
}
</script>
