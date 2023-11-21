<template>
  <v-container>
    <v-row>
      <!-- Column for Data Table -->
      <v-col cols="3">
        <v-card min-width="350" max-width="350">
          <v-card-title> Alerts </v-card-title>

          <v-divider></v-divider>

          <v-virtual-scroll :items="signalInstances" height="800">
            <template v-for="(item, index) in signalInstances" :key="item.id">
              <div class="pa-2" :class="index % 2 === 0 ? 'bg-grey-lighten-2' : ''">
                {{ item.signal.name }}
                <!-- Other data fields... -->
                <v-btn icon variant="text" @click="selectItem(item)">
                  <v-icon>mdi-play-circle-outline</v-icon>
                </v-btn>
              </div>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-col>
      <!-- Column for Raw Signal Viewer -->
      <v-col cols="9">
        <raw-signal-viewer2 class="fill-width" :value="selectedItem" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, toRefs, watch } from "vue"
import { formatRelativeDate, formatDate } from "@/filters"
import SignalPopover from "@/signal/SignalPopover.vue"
import RawSignalViewer2 from "@/signal/NewRawSignalViewer2.vue"
import WorkflowRunModal from "@/workflow/RunModal.vue"
import { useRoute, useRouter } from "vue-router"

export default {
  name: "SignalInstanceTab",
  components: {
    SignalPopover,
    RawSignalViewer2,
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
    selectedSignalId: String,
  },
  setup(props) {
    const { modelValue, loading } = toRefs(props)
    const signalInstances = ref(props.modelValue)
    const internalLoading = ref(props.loading)

    // Reactive property for selected item
    const selectedItem = ref({})

    const router = useRouter()

    console.log("Got signalInstances", signalInstances)

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

    // Method to update the selected item
    const selectItem = (item) => {
      console.log("Got item", item)
      selectedItem.value = item
      router.push({ name: "SignalDetails", params: { id: item.raw.id } })
    }

    watch(
      () => props.selectedSignalId,
      (id) => {
        if (id) {
          const selectedSignal = signalInstances.value.find((signal) => signal.id === id)
          if (selectedSignal) {
            selectItem(selectedSignal)
          }
        }
      }
    )

    return {
      formatRelativeDate,
      formatDate,
      signalInstances,
      headers,
      showRun,
      internalLoading,
      selectedItem,
      selectItem,
    }
  },
}
</script>

<style scoped>
.fill-width {
  width: 100%;
}

.overflow-auto {
  overflow: auto;
}
</style>
