<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, onMounted, onUpdated } from "vue"
import CaseApi from "@/case/api"
import AvatarStack from "@/components/AvatarStack.vue"
import CaseToggleVisibility from "@/case/CaseToggleVisibility.vue"
import SearchPopoverMenu2 from "@/components/SearchPopoverMenu2.vue"
import SearchPopoverStatus from "@/components/SearchPopoverStatus.vue"
import SearchPopoverParticipant from "@/components/SearchPopoverParticipant.vue"
import CustomMenuInput from "@/components/CustomMenuInput.vue"

// Define the props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
    required: true,
  },
})

// Define the emits
const emit = defineEmits(["update:modelValue"])

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

// You can directly return the setup variables
</script>

<template>
  <v-navigation-drawer location="right" width="400">
    <!-- <v-toolbar density="compact" color="transparent">
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
      <case-toggle-visibility v-model="visibility" />
    </v-toolbar> -->
    <div class="pl-6">
      <v-row no-gutters align="center" class="pt-6">
        <v-col cols="2">
          <div class="text-subtitle-2 font-weight-regular">Status</div>
        </v-col>
        <v-col cols="4">
          <!-- <search-popover-menu
            :priority="modelValue.case_priority?.name"
            @priority-selected="handlePriorityChange"
            class="pl-4"
          /> -->
          <SearchPopoverStatus
            :status="modelValue.status"
            @status-selected="handlePriorityChange"
            class="pl-4"
          />
        </v-col>
      </v-row>
      <v-row no-gutters align="center" class="pt-6">
        <v-col cols="2">
          <div class="text-subtitle-2 font-weight-regular">Priority</div>
        </v-col>
        <v-col cols="4">
          <SearchPopoverMenu2
            :priority="modelValue.case_priority?.name"
            @priority-selected="handlePriorityChange"
            class="pl-4"
          />
        </v-col>
      </v-row>
      <v-row no-gutters align="center" class="pt-6">
        <v-col cols="2">
          <div class="text-subtitle-2 font-weight-regular">Assignee</div>
        </v-col>
        <v-col cols="4">
          <SearchPopoverParticipant
            :participant="modelValue.assignee?.individual.name"
            @status-selected="handlePriorityChange"
            class="pl-4"
          />
        </v-col>
      </v-row>
      <v-row no-gutters align="center" class="pt-6">
        <v-col cols="2">
          <div class="text-subtitle-2 font-weight-regular">Labels</div>
        </v-col>
        <v-col cols="8">
          <SearchPopoverMenu2
            :priority="modelValue.case_priority?.name"
            @priority-selected="handlePriorityChange"
            class="pl-4"
          />
        </v-col>
      </v-row>
    </div>
    <v-divider class="mt-8"></v-divider>

    <div class="pl-6">
      <!-- Render each resource type in the sidebar -->
      <v-row class="pt-6">
        <v-col cols="8">
          <v-btn
            class="text-subtitle-2 font-weight-regular"
            prepend-icon="mdi-jira"
            variant="text"
            block
          >
            Ticket
          </v-btn>
        </v-col>
      </v-row>

      <!-- <v-row no-gutters class="pt-6">
        <v-col cols="2">
          <div class="text-subtitle-2 font-weight-regular">Conversation</div>
        </v-col>
        <v-col cols="8">
          <div class="pl-4">{{ modelValue.conversation?.description }}</div>
          <v-icon> </v-icon>
        </v-col>
      </v-row> -->

      <v-row no-gutters class="pt-6">
        <v-col cols="8">
          <v-btn
            class="text-subtitle-2 font-weight-regular"
            prepend-icon="mdi-slack"
            variant="text"
            block
          >
            Conversation
          </v-btn>
        </v-col>
      </v-row>

      <v-row no-gutters class="pt-6">
        <v-col cols="8">
          <v-btn
            class="text-subtitle-2 font-weight-regular"
            prepend-icon="mdi-file-document"
            variant="text"
            block
          >
            Document
          </v-btn>
        </v-col>
      </v-row>

      <v-row no-gutters class="pt-6">
        <v-col cols="8">
          <v-btn
            class="text-subtitle-2 font-weight-regular"
            prepend-icon="mdi-folder-google-drive"
            variant="text"
            block
          >
            Storage
          </v-btn>
        </v-col>
      </v-row>

      <!-- Add similar blocks for other resources as needed -->
      <!-- ... -->
    </div>
  </v-navigation-drawer>
</template>
