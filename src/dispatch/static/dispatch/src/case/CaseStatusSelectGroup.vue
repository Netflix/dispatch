<template>
  <v-item-group mandatory>
    <v-dialog v-model="dialogVisible" max-width="600">
      <v-card>
        <v-card-title>Update Case Status</v-card-title>
        <v-card-text>
          Are you sure you want to change the case status from {{ modelValue.status }} to
          {{ selectedStatus }}
        </v-card-text>
        <v-btn
          class="ml-6 mb-4"
          size="small"
          color="info"
          elevation="1"
          @click="changeStatus(selectedStatus)"
        >
          Submit
        </v-btn>
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
    label: "Resolved",
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
  selectedStatus.value = newStatus
  dialogVisible.value = true
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
