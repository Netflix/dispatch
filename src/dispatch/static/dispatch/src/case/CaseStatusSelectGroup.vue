<template>
  <v-item-group mandatory>
    <v-dialog v-model="dialogVisible" max-width="600">
      <v-card>
        <v-card-title>Update Case Status</v-card-title>
        <v-card-text>
          Are you sure you want to change the case status from {{ _case.status }} to
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
                <FancyTooltip :text="status.tooltip" hotkeys="">
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
                </FancyTooltip>
              </v-sheet>
            </div>
          </v-item>
        </v-col>
      </v-row>
    </v-container>
  </v-item-group>
</template>

<script>
import { mapActions } from "vuex"
import FancyTooltip from "@/components/FancyTooltip.vue"

export default {
  name: "CaseStatusSelectGroup",
  props: {
    _case: {
      type: Object,
      required: false,
      default: () => ({}),
    },
  },
  components: {
    FancyTooltip,
  },
  data() {
    return {
      selectedStatus: null,
      dialogVisible: false,
    }
  },
  computed: {
    statuses() {
      return [
        {
          name: "New",
          label: "New",
          color: "red",
          hoverClass: "hover-card-three",
          sheetClass: "rounded-s-xl arrow",
          tooltip: this._case.created_at,
        },
        {
          name: "Triage",
          label: "Triaged",
          color: "red",
          hoverClass: "hover-card-two",
          sheetClass: "arrow",
          tooltip: this._case.triage_at,
        },
        {
          name: "Closed",
          label: "Resolved",
          color: "green",
          hoverClass: "hover-card",
          sheetClass: "arrow",
          tooltip: this._case.closed_at,
        },
        {
          name: "Escalated",
          label: "Escalated",
          color: "red",
          hoverClass: "",
          sheetClass: "rounded-e-xl end-sheet",
          tooltip: this._case.escalated_at,
        },
      ]
    },
  },
  methods: {
    ...mapActions("case_management", ["save_page"]),
    changeStatus(newStatus) {
      this._case.status = newStatus
      this.save_page()
      this.dialogVisible = false
      this.selectedStatus = null
    },
    openDialog(newStatus) {
      this.selectedStatus = newStatus
      this.dialogVisible = true
    },
    isActiveStatus(status) {
      return this._case.status === status
    },
  },
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
