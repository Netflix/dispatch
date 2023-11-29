<template>
  <v-container>
    <v-row>
      <!-- Column for Data Table -->
      <v-col cols="3">
        <v-card min-width="350" max-width="350" class="signal-card" elevation="0">
          <v-card-title> Alerts </v-card-title>

          <v-divider></v-divider>

          <v-virtual-scroll :items="signalInstances" height="800">
            <template v-slot:default="{ item }">
              <div class="d-flex align-center">
                <hover-card :item="item">
                  <span style="font-size: 0.75rem">
                    {{ item.signal.name }}
                  </span>
                </hover-card>
                <span style="font-size: 0.75rem" class="pl-1">
                  · {{ formatRelativeDate(item.created_at) }}
                </span>
                <!-- Other data fields... -->
                <v-btn icon dense size="x-small" variant="text" @click="selectItem(item)">
                  <v-icon size="medium">mdi-play-circle-outline</v-icon>
                </v-btn>
              </div>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-col>
      <!-- Column for Raw Signal Viewer -->
      <v-col cols="9">
        <v-card elevation="0" class="signal-card pt-2">
          <span style="font-size: 0.75rem">
            <!-- {{ selectedItem.signal.name }} -->
          </span>
          <raw-signal-viewer :value="selectedItem" />
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, withDefaults, toRef } from "vue"
import { useRoute, useRouter } from "vue-router"
import { formatRelativeDate } from "@/filters"

import RawSignalViewer from "@/signal/NewRawSignalViewer.vue"
import HoverCard from "@/components/HoverCard.vue"

// Define props
const props = withDefaults(
  defineProps<{
    modelValue: {
      type: any[]
      required: true
    }
    loading: {
      type: boolean
      default: false
      required: true
    }
    selectedSignalId: string
  }>(),
  {
    modelValue: [],
    loading: false,
  }
)

const signalInstances = toRef(props, "modelValue")
const internalLoading = toRef(props, "loading")
const signalIdToIndexMap = ref({})
const selectedItem = ref(signalInstances.value[0])

const router = useRouter()
const route = useRoute()

watch(
  () => props.modelValue,
  (newValue) => {
    signalInstances.value = newValue
  }
)

watch(
  () => props.loading,
  (newValue) => {
    internalLoading.value = newValue
  }
)

const headers = ref([
  { title: "Signal", key: "signal", sortable: false },
  { title: "Created At", key: "created_at" },
  { title: "", key: "data-table-actions", sortable: false, align: "end" },
])

const selectItem = (item) => {
  console.log("Got item", item)
  selectedItem.value = item
  router.push({ name: "SignalDetails", params: { signal_id: item.raw.id } })
}

watch(
  [signalInstances, () => route.params],
  ([newSignalInstances, newParams]) => {
    signalIdToIndexMap.value = newSignalInstances.reduce((map, signal, index) => {
      map[signal.raw.id] = index
      return map
    }, {})

    const newSignalId = newParams.signal_id
    const index = signalIdToIndexMap.value[newSignalId]
    if (index !== undefined) {
      selectedItem.value = newSignalInstances[index]
    }
  },
  { immediate: true, deep: true }
)
</script>

<style scoped>
.signal-card {
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 8px !important;
}
</style>
