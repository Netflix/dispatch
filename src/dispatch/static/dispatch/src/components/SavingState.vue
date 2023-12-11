<template>
  <div>
    <v-progress-circular
      v-if="saving"
      indeterminate
      size="14"
      color="grey-lighten-1"
      class="pl-6"
    />
    <v-icon size="x-small" class="pl-4" v-else>mdi-check</v-icon>
    <span class="pl-4 dispatch-text-subtitle">updated {{ formattedUpdatedAt }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, watchEffect } from "vue"
import { formatDistanceToNow, parseISO } from "date-fns"
import { useSavingState } from "@/composables/useSavingState"

const { saving } = useSavingState()
let formattedUpdatedAt = ref("")
let updatedAtRef = ref("")

watchEffect(() => {
  if (updatedAtRef.value) {
    formattedUpdatedAt.value = formatDistanceToNow(parseISO(updatedAtRef.value)) + " ago"
  }
})

watch(saving, (newVal, oldVal) => {
  if (oldVal === true && newVal === false) {
    updatedAtRef.value = new Date().toISOString()
  }
})

const props = defineProps({
  updatedAt: {
    type: String,
    required: true,
  },
})

watch(
  () => props.updatedAt,
  (newVal) => {
    if (newVal) {
      updatedAtRef.value = newVal
    }
  }
)
</script>
