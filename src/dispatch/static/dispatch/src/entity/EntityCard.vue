<template>
  <v-card class="position-relative">
    <v-row>
      <v-col cols="8" style="align-self: center">
        <v-card-title class="pb-0 mb-0">{{ entity.entity_type.name }}</v-card-title>
      </v-col>
      <v-col class="text-right" cols="4" v-if="count > 1" style="align-self: center">
        <v-tooltip location="bottom">
          <template #activator="{ props }">
            <span v-bind="props">
              <v-badge color="grey" :content="badgeCount" offset-x="45" offset-y="37">
                <v-card-subtitle />
              </v-badge>
            </span>
          </template>
          <span>This entity has been seen {{ count }} times in this case</span>
        </v-tooltip>
      </v-col>
    </v-row>
    <v-card-text style="font-size: 18px">{{ entity.value }}</v-card-text>
    <v-divider />
    <v-hover>
      <template #default="{ hover }">
        <v-card
          color="red-lighten-5"
          rounded="xl"
          class="d-flex align-center mx-4 mt-3 mb-3"
          :elevation="hover ? 2 : 0"
          @click="openSignalInstanceTab"
        >
          <v-card-text class="d-flex align-center">
            <v-progress-linear v-if="isLoading" height="3" color="red-lighten-1" indeterminate />
            <span v-else>
              <span v-if="signalInstanceCount > 1">
                Seen in
                <span :class="{ 'font-weight-bold': signalInstanceCount > 5 }">{{
                  signalInstanceCount
                }}</span>
                other signals
              </span>
              <span v-else> First time this entity has been seen in a signal </span>
            </span>
          </v-card-text>
        </v-card>
      </template>
    </v-hover>
    <v-hover>
      <template #default="{ hover }">
        <v-card
          color="red-lighten-5"
          rounded="xl"
          class="d-flex align-center mx-4 mt-3 mb-3"
          :elevation="hover ? 2 : 0"
          @click="openCaseTab"
        >
          <v-card-text class="d-flex align-center">
            <v-progress-linear v-if="isLoading" height="3" color="red-lighten-1" indeterminate />
            <span v-else>
              <span v-if="caseCount > 1">
                Seen in
                <span :class="{ 'font-weight-bold': caseCount > 5 }">{{ caseCount }}</span>
                other cases
              </span>
              <span v-else> First time this entity has been seen in a case </span>
            </span>
          </v-card-text>
        </v-card>
      </template>
    </v-hover>
    <v-dialog v-model="signalDialog" max-width="1080">
      <signal-instance-tab :inputSignalInstances="signalInstances" />
    </v-dialog>
    <v-dialog v-model="caseDialog" max-width="1080">
      <case-tab :inputCases="cases" />
    </v-dialog>
  </v-card>
</template>

<script>
import { mapFields } from "vuex-map-fields"

import CaseTab from "@/case/CaseTab.vue"
import EntityApi from "@/entity/api"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"

export default {
  name: "EntityCard",
  props: {
    entity: {
      type: Object,
      required: true,
    },
    count: {
      type: Number,
      default: 1,
    },
    selectedDateTime: {
      type: Number,
      required: true,
    },
  },
  components: {
    "signal-instance-tab": SignalInstanceTab,
    "case-tab": CaseTab,
  },
  computed: {
    ...mapFields("entity", ["dialogs.showCaseView"]),
    badgeCount() {
      return this.count >= 100 ? "x99+" : `x${this.count}`
    },
  },
  data() {
    return {
      caseCount: null,
      signalInstanceCount: null,
      isLoading: true,
      signalDialog: false,
      caseDialog: false,
      signalInstances: [],
      cases: [],
    }
  },
  async mounted() {
    await this.refreshData()
  },
  watch: {
    selectedDateTime() {
      this.refreshData()
    },
  },
  methods: {
    async refreshData() {
      try {
        this.isLoading = true

        const casePromise = EntityApi.getCases(this.entity.id, this.selectedDateTime).then(
          (response) => response.data
        )
        const signalPromise = EntityApi.getSignalInstances(
          this.entity.id,
          this.selectedDateTime
        ).then((response) => response.data)

        const [casesResponse, signalResponse] = await Promise.all([casePromise, signalPromise])

        this.cases = casesResponse.cases
        this.caseCount = this.cases.length

        this.signalInstances = signalResponse.instances
        this.signalInstanceCount = this.signalInstances.length

        this.isLoading = false
      } catch (error) {
        console.error("Error in refreshData:", error)
      }
    },
    async openSignalInstanceTab() {
      this.signalDialog = true
      this.$nextTick(() => {
        this.$refs.signalInstanceTab = this.signalInstances
      })
    },
    async openCaseTab() {
      this.caseDialog = true
      this.$nextTick(() => {
        this.$refs.caseTab = this.cases
      })
    },
    getStartDate() {
      return new Date(Date.now() - this.selectedDateTime * 86400000).toISOString()
    },
  },
}
</script>
