<template>
  <v-item-group mandatory>
    <v-dialog v-model="dialogVisible" max-width="500">
      <v-card>
        <v-card-title>Update Case Status</v-card-title>
        <v-card-text
          >Are you sure you want to change the case status from {{ _case.status }} to
          {{ newStatus }}</v-card-text
        >
        <v-btn class="ml-6 mb-4" small color="info" elevation="1" @click="changeStatus(newStatus)">
          Submit
        </v-btn>
      </v-card>
    </v-dialog>
    <v-container fluid>
      <v-row no-gutters>
        <v-col cols="6" md="2">
          <v-item v-slot="{ active, toggle }">
            <div class="overlap-card hover-card-three" @click="openDialog('New')">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-sheet outlined color="grey lighten-1" class="rounded-l-xl arrow">
                    <v-card
                      class="d-flex align-center card-with-arrow rounded-l-xl arrow"
                      height="25"
                      width="100%"
                      @click="toggle"
                      flat
                      color="grey lighten-4"
                      v-bind="attrs"
                      v-on="on"
                    >
                      <v-scroll-y-transition>
                        <div v-if="isActiveStatus('New')" class="flex-grow-1 text-center">
                          <v-badge color="red" dot left offset-x="-10" offset-y="0"> </v-badge>New
                        </div>
                        <div v-else class="flex-grow-1 text-center text--disabled">New</div>
                      </v-scroll-y-transition>
                    </v-card>
                  </v-sheet>
                </template>
                <span>{{ _case.created_at }}</span>
              </v-tooltip>
            </div>
          </v-item>
        </v-col>

        <v-col cols="6" md="2">
          <v-item v-slot="{ active, toggle }">
            <div class="overlap-card hover-card-two" @click="openDialog('Triage')">
              <v-sheet outlined color="grey lighten-1" class="arrow">
                <v-card
                  class="d-flex align-center arrow"
                  height="25"
                  width="100%"
                  @click="toggle"
                  outlined
                  color="grey lighten-4"
                >
                  <v-scroll-y-transition>
                    <div v-if="isActiveStatus('Triage')" class="flex-grow-1 text-center">
                      <v-badge color="red" dot left offset-x="-10" offset-y="0"></v-badge
                      >Investigating
                    </div>
                    <div v-else class="flex-grow-1 text-center text--disabled">Investigating</div>
                  </v-scroll-y-transition>
                </v-card>
              </v-sheet>
            </div>
          </v-item>
        </v-col>

        <v-col cols="6" md="2">
          <v-item v-slot="{ active, toggle }">
            <div class="overlap-card hover-card" @click="openDialog('Resolved')">
              <v-sheet outlined color="grey lighten-1" class="arrow">
                <v-card
                  class="d-flex align-center arrow"
                  height="25"
                  width="100%"
                  @click="toggle"
                  outlined
                  color="grey lighten-4"
                >
                  <v-scroll-y-transition>
                    <div v-if="isActiveStatus('Resolved')" class="flex-grow-1 text-center">
                      <v-badge color="red" dot left offset-x="-10" offset-y="0"></v-badge>Resolved
                    </div>
                    <div v-else class="flex-grow-1 text-center text--disabled">Resolved</div>
                  </v-scroll-y-transition>
                </v-card>
              </v-sheet>
            </div>
          </v-item>
        </v-col>

        <v-col cols="6" md="2">
          <v-item v-slot="{ active, toggle }">
            <div class="overlap-card" @click="openDialog('Escalated')">
              <v-sheet outlined color="grey lighten-1" class="rounded-r-xl">
                <v-card
                  class="d-flex align-center rounded-r-xl"
                  height="25"
                  width="100%"
                  @click="toggle"
                  outlined
                  color="grey lighten-4"
                >
                  <v-scroll-y-transition>
                    <div v-if="isActiveStatus('Escalated')" class="flex-grow-1 text-center">
                      <v-badge color="red" dot left offset-x="-10" offset-y="0"></v-badge>Escalated
                    </div>
                    <div v-else class="flex-grow-1 text-center text--disabled">Escalated</div>
                  </v-scroll-y-transition>
                </v-card>
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

export default {
  name: "CaseStatusSelectGroup",
  props: {
    _case: {
      type: Object,
      required: false,
      default: () => ({}), // returns an empty object if _case is not provided
    },
  },
  data() {
    return {
      dialogVisible: false,
      newStatus: "",
    }
  },
  methods: {
    ...mapActions("case_management", ["save_page"]),
    changeStatus(newStatus) {
      this._case.status = newStatus
      this.save_page()
    },
    openDialog(newStatus) {
      this.newStatus = newStatus
      this.dialogVisible = true
    },
    isActiveStatus(status) {
      console.log(this._case.status, status)
      console.log(typeof this._case.status, typeof status)
      console.log(this._case.status === status)
      return this._case.status === status
    },
  },
}
</script>

<style scoped>
.refactoring-ui-shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.arrow {
  clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%);
}

.overlap-card {
  margin-left: -15px;
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
