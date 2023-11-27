<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, onUpdated, watchEffect } from "vue"
import CaseApi from "@/case/api"
import SearchPopoverCasePriority from "@/components/SearchPopoverCasePriority.vue"
import SearchPopoverStatus from "@/components/SearchPopoverStatus.vue"
import SearchPopoverParticipant from "@/components/SearchPopoverParticipant.vue"

// Define the props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
    required: true,
  },
  open: {
    type: Boolean,
    default: true,
  },
})

// Define the emits
const emit = defineEmits(["update:modelValue", "update:open"])
const drawerVisible = ref(props.open)

watchEffect(() => {
  drawerVisible.value = props.open
})

watchEffect(() => {
  emit("update:open", drawerVisible.value)
})
// Setup
const isMenuOpen = ref(false)
const participants = computed({
  get: () => props.modelValue.participants,
  set: (value) => emit("update:modelValue", value),
})

const visibility = computed({
  get: () => props.modelValue.visibility,
  set: (value) => emit("update:modelValue", value),
})

onUpdated(() => {
  console.log("Got case", props.modelValue)
})

const handlePriorityChange = async (newPriority: string) => {
  // Check for case ID
  if (!props.modelValue.id) {
    console.error("Case ID is missing")
    return
  }

  try {
    // Update the case with the new priority
    const updatedCase = await CaseApi.update(props.modelValue.id, {
      ...props.modelValue,
      priority: newPriority,
    })

    // Emit an event to update the parent component's modelValue
    // emit("update:modelValue", updatedCase)

    // Optionally, show a success notification
  } catch (error) {
    console.error("Error updating case priority:", error)
    // Optionally, handle the error, such as showing an error notification
  }
}
</script>

<template>
  <div>
    <v-navigation-drawer v-model="drawerVisible" location="right" width="400">
      <v-divider></v-divider>

      <div class="pl-6">
        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="2">
            <div class="dispatch-font">Assignee</div>
          </v-col>
          <v-col cols="10">
            <SearchPopoverParticipant
              :participant="modelValue.assignee?.individual.name"
              type="assignee"
              label="Assign to..."
              tooltip-label="Update Assignee"
              hotkey="a"
              @status-selected="handlePriorityChange"
              class="pl-4"
            />
          </v-col>
        </v-row>
        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="2">
            <div class="dispatch-font">Reporter</div>
          </v-col>
          <v-col cols="10">
            <SearchPopoverParticipant
              :participant="modelValue.reporter?.individual.name"
              type="reporter"
              label="Set reporter to..."
              tooltip-label="Update Reporter"
              hotkey="r"
              @status-selected="handlePriorityChange"
              class="pl-4"
            />
          </v-col>
        </v-row>
        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="2">
            <div class="dispatch-font">Status</div>
          </v-col>
          <v-col cols="10">
            <SearchPopoverStatus
              :status="modelValue.status"
              @status-selected="handlePriorityChange"
              class="pl-4"
            />
          </v-col>
        </v-row>
        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="2">
            <div class="dispatch-font">Priority</div>
          </v-col>
          <v-col cols="10">
            <SearchPopoverCasePriority
              :priority="modelValue.case_priority?.name"
              @priority-selected="handlePriorityChange"
              class="pl-4"
            />
          </v-col>
        </v-row>
      </div>
      <v-divider class="mt-8"></v-divider>

      <!-- <div class="pl-3">
        <v-row class="pt-6" align="center">
          <v-col cols="8">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              prepend-icon="mdi-jira"
              variant="text"
              :href="modelValue.ticket.weblink"
            >
              Ticket
            </v-btn>
          </v-col>
        </v-row>

        <v-row no-gutters class="pt-6" align="center">
          <v-col cols="8">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              prepend-icon="mdi-slack"
              variant="text"
              :href="modelValue.conversation.weblink"
            >
              Conversation
            </v-btn>
          </v-col>
        </v-row>

        <v-row no-gutters class="pt-6" align="center">
          <v-col cols="8">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              prepend-icon="mdi-file-document"
              variant="text"
              :href="modelValue.documents.weblink"
            >
              Document
            </v-btn>
          </v-col>
        </v-row>

        <v-row no-gutters class="pt-6" align="center">
          <v-col cols="8">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              prepend-icon="mdi-folder-google-drive"
              variant="text"
              :href="modelValue.storage.weblink"
            >
              Storage
            </v-btn>
          </v-col>
        </v-row>
      </div> -->
    </v-navigation-drawer>
  </div>
</template>

<style scope>
.dispatch-font {
  color: rgb(107, 111, 118) !important;
  font-size: 0.8125rem !important;
  font-weight: 500;
}
</style>
