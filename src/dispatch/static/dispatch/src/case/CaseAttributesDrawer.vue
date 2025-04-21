<script setup lang="ts">
import { ref, defineProps, watchEffect, watch } from "vue"
import { debounce } from "lodash"

import CaseApi from "@/case/api"
import CaseResolutionSearchPopover from "@/case/CaseResolutionSearchPopover.vue"
import CasePrioritySearchPopover from "@/case/priority/CasePrioritySearchPopover.vue"
import CaseSeveritySearchPopover from "@/case/severity/CaseSeveritySearchPopover.vue"
import CaseTypeSearchPopover from "@/case/type/CaseTypeSearchPopover.vue"
import DTooltip from "@/components/DTooltip.vue"
import ParticipantSearchPopover from "@/participant/ParticipantSearchPopover.vue"
import ProjectSearchPopover from "@/project/ProjectSearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"

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
const { setSaving } = useSavingState()
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

const saveCaseDetails = async () => {
  try {
    setSaving(true)
    await CaseApi.update(modelValue.value.id, modelValue.value)
    setSaving(false)
  } catch (e) {
    console.error("Failed to save case details", e)
  }
}

const debouncedSave = debounce(saveCaseDetails, 1000)

const handleResolutionUpdate = (newResolution) => {
  modelValue.value.resolution = newResolution
  emit("update:modelValue", { ...modelValue.value })
  debouncedSave()
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
              :project="modelValue.project?.name"
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
              :project="modelValue.project?.name"
              class="pl-6"
            />
          </v-col>
        </v-row>

        <v-row no-gutters align="center" class="pt-6">
          <v-col cols="1">
            <div class="dispatch-font">Type</div>
          </v-col>
          <v-col cols="10">
            <CaseTypeSearchPopover
              :case-type="modelValue.case_type?.name"
              :project="modelValue.project?.name"
              class="pl-6"
            />
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

      <div class="pl-6 pt-4 pr-6 d-flex align-center justify-space-between">
        <div class="d-flex align-center justify-start">
          <div class="dispatch-font-title pr-2">Resolution</div>
          <DTooltip
            text="Document your findings and provide the rationale for any decisions you made as part of this case."
            hotkeys=""
          >
            <template #activator="{ tooltip }">
              <v-btn
                v-bind="tooltip"
                variant="plain"
                density="compact"
                size="x-small"
                icon="mdi-information-outline"
              />
            </template>
          </DTooltip>
        </div>
        <CaseResolutionSearchPopover :case-resolution="modelValue.resolution_reason" />
      </div>
      <v-card flat color="grey-lighten-5" class="rounded-lg mt-4 ml-4 mr-4">
        <RichEditor
          :content="modelValue.resolution"
          @update:model-value="handleResolutionUpdate"
          style="min-height: 400px; margin: 10px; font-size: 0.9125rem; font-weight: 400"
        />
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
