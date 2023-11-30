<template>
  <v-container>
    <v-row>
      <!-- Column for Data Table -->
      <v-col cols="3">
        <v-card min-width="350" class="signal-card" elevation="0">
          <v-virtual-scroll :items="signalInstances" height="828" class="pt-2">
            <template #default="{ item }">
              <div class="d-flex align-center">
                <span style="font-size: 0.8rem" class="pl-8">
                  {{ item.signal.name }}
                </span>
                <span class="pl-1 dispatch-text-paragraph">
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
          <span class="dispatch-text-paragraph">
            <!-- {{ selectedItem.signal.name }} -->
          </span>
          <raw-signal-viewer :value="selectedItem" />
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, toRef } from "vue"
import { useRoute, useRouter } from "vue-router"
import { formatRelativeDate } from "@/filters"

import RawSignalViewer from "@/signal/NewRawSignalViewer.vue"

const props = defineProps({
  modelValue: {
    type: Array as () => any[],
    default: () => [],
    required: true,
  },
  loading: {
    type: Boolean,
    default: () => false,
    required: true,
  },
  selectedSignalId: {
    type: String,
    default: () => "",
  },
})

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

const selectItem = (item) => {
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

<style lang="scss" scoped>
@import "@/styles/index.scss";
.signal-card {
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 8px !important;
}
</style>
