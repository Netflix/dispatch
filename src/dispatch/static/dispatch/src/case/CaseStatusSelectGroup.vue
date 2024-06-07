<template>
  <v-item-group mandatory>
    <v-dialog v-model="dialogVisible" max-width="660">
      <v-card class="mx-auto">
        <v-card-title class="ml-2">Update Case Status</v-card-title>
        <v-card-text class="dispatch-text-title">
          Are you sure you want to change the case status from
          <v-chip size="small" class="ml-1 mr-1" :color="statusColors[modelValue.status]">
            {{ modelValue.status }}
          </v-chip>
          to
          <v-chip size="small" class="ml-1 mr-1" :color="statusColors[selectedStatus]">
            {{ selectedStatus }}
          </v-chip>
          ?
        </v-card-text>
        <v-card-actions class="pt-4">
          <v-spacer />

          <v-btn @click="changeStatus(selectedStatus)"> Submit </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="alreadySelectedDialog" max-width="600">
      <v-card class="mx-auto">
        <v-card-title class="ml-2">Status Not Changed</v-card-title>
        <v-card-text class="dispatch-text-title">
          This case was moved to the status
          <v-chip size="small" class="ml-1 mr-1" :color="statusColors[selectedStatus]">
            {{ selectedStatus }}
          </v-chip>
          on
          <DTooltip :text="formatToTimeZones(selectedStatusTooltip)" hotkeys="">
            <template #activator="{ tooltip }">
              <v-chip class="ml-1" v-bind="tooltip">
                {{ formatToUTC(selectedStatusTooltip) }}
              </v-chip>
            </template>
          </DTooltip>
        </v-card-text>
        <v-card-actions class="pt-4">
          <v-spacer />

          <v-btn @click="alreadySelectedDialog = false"> Dismiss </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-container fluid>
      <v-row no-gutters>
        <v-col v-for="status in statuses" :key="status.name" cols="6" md="2">
          <v-item v-slot="{ toggle }">
            <div class="overlap-card" :class="status.hoverClass" @click="openDialog(status.name)">
              <v-sheet variant="outlined" color="grey-lighten-1" :class="status.sheetClass">
                <DTooltip :text="status.tooltip" hotkeys="">
                  <template #activator="{ tooltip }">
                    <v-card
                      class="d-flex align-center"
                      :class="status.sheetClass"
                      height="30"
                      width="100%"
                      @click="toggle"
                      variant="flat"
                      color="grey-lighten-4"
                      v-bind="tooltip"
                    >
                      <v-scroll-y-transition>
                        <div
                          v-if="isActiveStatus(status.name)"
                          class="flex-grow-1 text-center dispatch-font-enabled"
                        >
                          <v-badge
                            :color="status.color"
                            bordered
                            dot
                            offset-x="10"
                            offset-y="-8"
                          />{{ status.label }}
                        </div>

                        <div v-else class="flex-grow-1 text-center text--disabled dispatch-font">
                          {{ status.label }}
                        </div>
                        <span>{{
                          status.tooltip ? status.tooltip : `Not yet ${status.label.toLowerCase()}`
                        }}</span>
                      </v-scroll-y-transition>
                    </v-card>
                  </template>
                </DTooltip>
              </v-sheet>
            </div>
          </v-item>
        </v-col>
      </v-row>
    </v-container>
  </v-item-group>
</template>

<script setup>
import { computed, watch, ref } from "vue"
import { useStore } from "vuex"
import { useSavingState } from "@/composables/useSavingState"
import { formatToUTC, formatToTimeZones } from "@/filters"
import DTooltip from "@/components/DTooltip.vue"
import CaseApi from "@/case/api"

const props = defineProps({
  modelValue: {
    type: Object,
    required: false,
    default: () => ({}),
  },
})

const store = useStore()
const { setSaving } = useSavingState()
let selectedStatus = ref(null)
let dialogVisible = ref(false)
let activeStatus = ref(props.modelValue.status)
let alreadySelectedDialog = ref(false)
let selectedStatusTooltip = ref(null)

const statuses = computed(() => [
  {
    name: "New",
    label: "Created",
    color: "red",
    hoverClass: "hover-card-three",
    sheetClass: "rounded-s-xl arrow",
    tooltip: props.modelValue.created_at,
  },
  {
    name: "Triage",
    label: "Triaged",
    color: "red",
    hoverClass: "hover-card-two",
    sheetClass: "arrow",
    tooltip: props.modelValue.triage_at,
  },
  {
    name: "Closed",
    label: "Closed",
    color: "green",
    hoverClass: "hover-card",
    sheetClass: "arrow",
    tooltip: props.modelValue.closed_at,
  },
  {
    name: "Escalated",
    label: "Escalated",
    color: "red",
    hoverClass: "",
    sheetClass: "rounded-e-xl end-sheet",
    tooltip: props.modelValue.escalated_at,
  },
])

const statusColors = computed(() => {
  const colorMap = {}
  statuses.value.forEach((status) => {
    colorMap[status.name] = status.color
  })
  return colorMap
})

const changeStatus = async (newStatus) => {
  const caseDetails = store.state.case_management.selected
  const previousStatus = activeStatus.value

  // Optimistically update the UI
  activeStatus.value = newStatus
  selectedStatus.value = null
  dialogVisible.value = false
  caseDetails.status = newStatus

  try {
    setSaving(true)
    await CaseApi.update(caseDetails.id, caseDetails)
    setSaving(false)
  } catch (e) {
    console.error(`Failed to update case status`, e)

    // If the API call fails, revert the active status change
    activeStatus.value = previousStatus

    store.commit(
      "notification_backend/addBeNotification",
      {
        text: `Failed to update case status`,
        type: "exception",
      },
      { root: true }
    )
  }
}

const openDialog = (newStatus) => {
  if (newStatus == "Escalated") {
    const caseDetails = store.state.case_management.selected
    store.dispatch("case_management/showEscalateDialog", caseDetails)
    return
  }
  const statusObj = statuses.value.find((status) => status.name === newStatus) // find the status object
  selectedStatus.value = newStatus
  selectedStatusTooltip.value = statusObj.tooltip // store the tooltip
  if (isActiveStatus(newStatus)) {
    alreadySelectedDialog.value = true
  } else {
    dialogVisible.value = true
  }
}

watch(
  () => props.modelValue.status,
  (newStatus) => {
    activeStatus.value = newStatus
  }
)

const isActiveStatus = (status) => {
  return activeStatus.value === status
}
</script>

<style scoped>
@import "@/styles/index.scss";

.arrow {
  clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%);
  padding-top: 1px;
  padding-left: 1px;
  padding-bottom: 1px;
  padding-right: 1px;
}

.end-sheet {
  padding-top: 1px;
  padding-left: 1px;
  padding-bottom: 1px;
  padding-right: 1px;
}
.overlap-card {
  margin-left: -20px;
  border-radius: 75%;
  box-shadow: 0 1px 3px 0px rgba(0, 0, 0, 0.1);
}
.overlap-card:first-child {
  margin-left: 0;
}
.overlap-card:last-child {
  margin-right: -20px;
}
.hover-card {
  position: relative;
  z-index: 1;
}
.hover-card-two {
  position: relative;
  z-index: 2;
}
.hover-card-three {
  position: relative;
  z-index: 3;
}

.dispatch-font {
  color: rgb(107, 111, 118) !important;
  font-size: 0.9125rem !important;
  font-weight: 400;
}

.dispatch-font-enabled {
  color: rgb(4, 4, 4) !important;
  font-size: 0.9125rem !important;
  font-weight: 500;
}

::v-deep .v-badge__badge {
  border-color: black !important;
}

::v-deep .v-badge--dot .v-badge__badge {
  border-color: black !important;
}
</style>
