<script setup lang="ts">
import { ref, defineProps, watchEffect, watch } from "vue"

import CaseApi from "@/case/api"
import CaseResolutionSearchPopover from "@/case/CaseResolutionSearchPopover.vue"
import CasePrioritySearchPopover from "@/case/priority/CasePrioritySearchPopover.vue"
import CaseSeveritySearchPopover from "@/case/severity/CaseSeveritySearchPopover.vue"
import CaseTypeSearchPopover from "@/case/type/CaseTypeSearchPopover.vue"
import ParticipantSearchPopover from "@/participant/ParticipantSearchPopover.vue"
import ProjectSearchPopover from "@/project/ProjectSearchPopover.vue"

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
// Create a local state for modelValue
const modelValue = ref({ ...props.modelValue })

watch(
  () => props.modelValue,
  (newVal) => {
    modelValue.value = newVal
  },
  { immediate: true }
)

watchEffect(() => {
  drawerVisible.value = props.open
})

watchEffect(() => {
  emit("update:open", drawerVisible.value)
})

const handleResolutionUpdate = (newResolution) => {
  modelValue.value.resolution = newResolution
  emit("update:modelValue", { ...modelValue.value }) // Emit the updated modelValue
  saveCaseDetails()
}

const saveCaseDetails = async () => {
  try {
    await CaseApi.update(modelValue.value.id, modelValue.value)
  } catch (e) {
    console.error("Failed to save case details", e)
  }
}
</script>

<template>
  <div>
    <v-navigation-drawer v-model="drawerVisible" location="right" width="400">
      <v-divider />

      <div class="pl-6">
        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="1">
            <div class="dispatch-font">Assignee</div>
          </v-col>
          <v-col cols="10">
            <ParticipantSearchPopover
              :participant="modelValue.assignee?.individual.name"
              type="assignee"
              label="Assign to..."
              tooltip-label="Update Assignee"
              hotkey="a"
              class="pl-8"
            />
          </v-col>
        </v-row>
        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="1">
            <div class="dispatch-font">Reporter</div>
          </v-col>
          <v-col cols="10">
            <ParticipantSearchPopover
              :participant="modelValue.reporter?.individual.name"
              type="reporter"
              label="Set reporter to..."
              tooltip-label="Update Reporter"
              hotkey="r"
              class="pl-8"
            />
          </v-col>
        </v-row>

        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="1">
            <div class="dispatch-font">Priority</div>
          </v-col>
          <v-col cols="10">
            <CasePrioritySearchPopover
              :case-priority="modelValue.case_priority?.name"
              class="pl-6"
            />
          </v-col>
        </v-row>

        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="1">
            <div class="dispatch-font">Severity</div>
          </v-col>
          <v-col cols="10">
            <CaseSeveritySearchPopover
              :case-severity="modelValue.case_severity?.name"
              class="pl-6"
            />
          </v-col>
        </v-row>

        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="1">
            <div class="dispatch-font">Type</div>
          </v-col>
          <v-col cols="10">
            <CaseTypeSearchPopover :case-type="modelValue.case_type?.name" class="pl-6" />
          </v-col>
        </v-row>

        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="1">
            <div class="dispatch-font">Project</div>
          </v-col>
          <v-col cols="10">
            <ProjectSearchPopover :project="modelValue.project?.name" class="pl-6" />
          </v-col>
        </v-row>
      </div>

      <v-divider class="mt-8 mb-8" />

      <div class="pl-3">
        <v-row no-gutters align="center">
          <v-col cols="8">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              prepend-icon="mdi-jira"
              variant="text"
              :disabled="!modelValue.ticket"
              :href="modelValue.ticket && modelValue.ticket.weblink"
              target="_blank"
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
              :disabled="!modelValue.conversation"
              :href="modelValue.conversation && modelValue.conversation.weblink"
              target="_blank"
            >
              Conversation
            </v-btn>
          </v-col>
        </v-row>

        <!-- For documents, consider the first document's weblink as an example -->
        <v-row no-gutters class="pt-6" align="center">
          <v-col cols="8">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              prepend-icon="mdi-file-document"
              variant="text"
              :disabled="!modelValue.documents.length"
              :href="modelValue.documents.length && modelValue.documents[0].weblink"
              target="_blank"
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
              :disabled="!modelValue.storage"
              :href="modelValue.storage && modelValue.storage.weblink"
              target="_blank"
            >
              Storage
            </v-btn>
          </v-col>
        </v-row>
      </div>

      <v-divider class="mt-8 mb-8" />

      <div class="pl-6 dispatch-font-title">Investigation Write-Up</div>
      <div class="pl-6 dispatch-font">
        Document your findings and provide the rationale for any decisions you made as part of this
        case.
      </div>

      <v-card flat color="grey-lighten-5" class="rounded-lg mt-6 ml-2 mr-2">
        <RichEditor
          :resolution="true"
          v-model="modelValue.resolution"
          @update:model-value="handleResolutionUpdate"
          style="min-height: 400px; margin: 10px; font-size: 0.9125rem; font-weight: 400"
        />
        <v-row class="pb-2 pr-4 pl-4">
          <v-col cols="12" class="d-flex justify-end align-center">
            <CaseResolutionSearchPopover
              :case-resolution="modelValue.resolution_reason"
              class="pl-6"
            />
          </v-col>
        </v-row>
      </v-card>
    </v-navigation-drawer>
  </div>
</template>

<style lang="scss" scoped>
@import "@/styles/index.scss";
.dispatch-font {
  color: rgb(107, 111, 118) !important;
  font-size: 0.8125rem !important;
  font-weight: 500;
}

.dispatch-font-title {
  color: rgb(20, 21, 22) !important;
  font-size: 1.2125rem !important;
  font-weight: 500;
}
</style>
