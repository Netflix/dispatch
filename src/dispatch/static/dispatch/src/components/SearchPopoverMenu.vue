<script setup lang="ts">
import { ref, onMounted, watch, watchEffect, defineEmits } from "vue"
import CasePriorityApi from "@/case/priority/api"
import type { Ref } from "vue"

const props = defineProps<{ priority: string }>()

const menu: Ref<boolean> = ref(false)
const priorities: Ref<string[]> = ref([])
const selectedPriority: Ref<string> = ref("")

const emit = defineEmits(["priority-selected"])

// Use watchEffect for immediate reactivity
watchEffect(() => {
  selectedPriority.value = props.priority || "Select Priority"
})

const fetchPriorities = async () => {
  try {
    const response = await CasePriorityApi.getAll()
    priorities.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching priorities:", error)
  }
}

onMounted(fetchPriorities)

watch(selectedPriority, (newValue: string) => {
  if (newValue && newValue !== props.priority) {
    console.log("Emitting event with new priority:", newValue)
    emit("priority-selected", newValue)
  }
})
</script>

<template>
  <div class="text-center">
    <v-menu v-model="menu" :close-on-content-click="false" location="end">
      <template v-slot:activator="{ props }">
        <v-btn
          class="text-subtitle-2 font-weight-regular"
          prepend-icon="mdi-check-circle"
          v-bind="props"
          variant="text"
        >
          {{ selectedPriority }}
        </v-btn>
      </template>

      <v-card min-width="300" class="rounded-lg">
        <v-autocomplete
          label="Change priority..."
          variant="underlined"
          class="pl-2 pr-2"
          :items="priorities"
          v-model="selectedPriority"
        ></v-autocomplete>
      </v-card>
    </v-menu>
  </div>
</template>
