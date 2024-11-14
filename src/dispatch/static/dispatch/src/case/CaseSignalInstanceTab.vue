<template>
  <v-container>
    <v-row>
      <!-- Column for Data Table -->
      <v-col cols="3" class="d-flex mr-n4">
        <v-card class="signal-card flex-card grey-bg" elevation="0">
          <v-virtual-scroll :items="signalInstances" height="828" class="pt-0">
            <template #default="{ item }">
              <div
                class="signal-list-item"
                :class="{ 'selected-row': selectedItem.raw.id === item.raw.id }"
                @click="selectItem(item)"
                role="button"
              >
                <div class="signal-info">
                  <span class="signal-name">
                    {{ item.signal.name }}
                  </span>
                  <span class="time-stamp"> · {{ formatRelativeDate(item.created_at) }} </span>
                </div>
              </div>
            </template>
          </v-virtual-scroll>
        </v-card>
      </v-col>
      <!-- Column for Raw Signal Viewer -->
      <v-col cols="9" class="d-flex">
        <v-card class="signal-card flex-card pt-2 pb-2" elevation="0">
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
@use "@/styles/index.scss" as *;

.signal-card {
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 8px !important;
}

.flex-card {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.signal-list-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  min-height: 48px;
  width: 100%;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }
}

.signal-info {
  display: flex;
  align-items: center;
  min-width: 0;
  flex: 1;
}

.signal-name {
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 65%;
}

.time-stamp {
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.6);
  white-space: nowrap;
  margin-left: 4px;
}

.grey-bg {
  background-color: rgb(244, 245, 248);
}

.selected-row {
  background-color: rgb(254, 255, 254);
}
</style>
