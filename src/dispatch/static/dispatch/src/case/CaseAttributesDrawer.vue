<script setup lang="ts">
import { ref, defineProps, watchEffect } from "vue"

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
const resolutionReasons = ref(["False Positive", "User Acknowledged", "Mitigated", "Escalated"])

watchEffect(() => {
  drawerVisible.value = props.open
})

watchEffect(() => {
  emit("update:open", drawerVisible.value)
})

const onSelectReason = async (reason: string) => {
  props.modelValue.resolution_reason = reason
  await CaseApi.update(props.modelValue.id, props.modelValue)
  // other logic as necessary
}
</script>

<template>
  <div>
    <v-navigation-drawer v-model="drawerVisible" location="right" width="400">
      <v-divider></v-divider>

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

      <v-divider class="mt-8 mb-8"></v-divider>
      <div class="pl-6 dispatch-font-title">Investigation Write-Up</div>
      <div class="pl-6 dispatch-font">
        Document your findings and provide the rationale for any decisions you made as part of this
        case.
      </div>

      <v-card flat color="grey-lighten-5" class="rounded-lg mt-6 ml-2 mr-2">
        <tiptap
          :resolution="true"
          v-model="modelValue.resolution"
          style="min-height: 400px; margin: 10px; font-size: 0.9125rem; font-weight: 400"
        ></tiptap>
        <v-row class="pb-2 pr-4 pl-4">
          <v-col cols="8" class="d-flex align-center">
            <CaseResolutionSearchPopover
              :case-resolution="modelValue.resolution_reason"
              class="pl-6"
            />
          </v-col>
          <!-- <v-col cols="4" class="d-flex justify-end align-center">
            <v-btn variant="text" elevation="1" @click="onSubmit()" class="dispatch-button-out">
              Submit
            </v-btn>
          </v-col> -->
        </v-row>
      </v-card>
      <v-divider class="mt-8 mb-8"></v-divider>

      <div class="pl-3">
        <v-row align="center">
          <v-col cols="8">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              prepend-icon="mdi-jira"
              variant="text"
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
            >
              Storage
            </v-btn>
          </v-col>
        </v-row>
      </div>
    </v-navigation-drawer>
  </div>
</template>

<style scope>
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

.dispatch-button-out {
  text-transform: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0px !important;
  font-weight: 500px !important;
  line-height: normal !important;
  transition-property: border, background-color, color, opacity !important;
  transition-duration: 0.15s !important;
  user-select: none !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px !important;
  background-color: rgb(255, 255, 255) !important;
  border: 1px solid rgb(223, 225, 228) !important;
  border-radius: 4px !important;
  color: rgb(60, 65, 73) !important;
  min-width: 28px !important;
  height: 28px !important;
  padding: 0px 14px !important;
  font-size: 0.75rem !important;
}
</style>
