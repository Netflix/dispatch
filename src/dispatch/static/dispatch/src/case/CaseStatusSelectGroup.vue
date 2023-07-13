<template>
  <v-item-group mandatory>
    <v-dialog v-model="selectedStatus" max-width="500">
      <v-card>
        <v-card-title>Update Case Status</v-card-title>
        <v-card-text
          >Are you sure you want to change the case status from {{ _case.status }} to
          {{ selectedStatus }}</v-card-text
        >

        <v-time-picker format="ampm" landscape scrollable></v-time-picker>
        <v-btn
          class="ml-6 mb-4"
          small
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
          <v-item v-slot="{ active, toggle }">
            <div class="overlap-card" :class="status.hoverClass" @click="openDialog(status.name)">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-sheet outlined color="grey lighten-1" :class="status.sheetClass">
                    <v-card
                      class="d-flex align-center"
                      :class="status.sheetClass"
                      height="30"
                      width="100%"
                      @click="toggle"
                      flat
                      color="grey lighten-4"
                      v-bind="attrs"
                      v-on="on"
                    >
                      <v-scroll-y-transition>
                        <div v-if="isActiveStatus(status.name)" class="flex-grow-1 text-center">
                          <v-badge
                            :color="status.color"
                            bordered
                            dot
                            left
                            offset-x="-10"
                            offset-y="0"
                          >
                          </v-badge
                          >{{ status.label }}
                        </div>

                        <div v-else class="flex-grow-1 text-center text--disabled">
                          {{ status.label }}
                        </div>
                        <span>{{
                          status.tooltip ? status.tooltip : `Not yet ${status.label.toLowerCase()}`
                        }}</span>
                      </v-scroll-y-transition>
                    </v-card>
                  </v-sheet>
                </template>
                <span>{{
                  status.tooltip ? status.tooltip : `Not yet ${status.label.toLowerCase()}`
                }}</span>
              </v-tooltip>
            </div>
          </v-item>
        </v-col>
      </v-row>
    </v-container>
  </v-item-group>
</template>

<script>
import { mapActions } from "vuex"

export default {
  name: "CaseStatusSelectGroup",
  props: {
    _case: {
      type: Object,
      required: false,
      default: () => ({}),
    },
  },
  data() {
    return {
      selectedStatus: null,
      statuses: [
        {
          name: "New",
          label: "New",
          color: "red",
          hoverClass: "hover-card-three",
          sheetClass: "rounded-l-xl arrow",
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
          sheetClass: "rounded-r-xl",
          tooltip: this._case.escalated_at,
        },
      ],
    }
  },
  methods: {
    ...mapActions("case_management", ["save_page"]),
    changeStatus(newStatus) {
      this._case.status = newStatus
      this.save_page()
      this.selectedStatus = null
    },
    openDialog(newStatus) {
      this.selectedStatus = newStatus
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
}

.overlap-card {
  margin-left: -15px;
  border-radius: 75%;
  box-shadow: 0 1px 6px 0px rgba(0, 0, 0, 0.1);
}

.overlap-card:first-child {
  margin-left: 0;
}

.overlap-card:last-child {
  margin-right: -15px;
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
</style>
