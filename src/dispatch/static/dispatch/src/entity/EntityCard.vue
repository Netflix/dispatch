<template>
  <v-card elevation="1" outlined class="position-relative">
    <v-card-title>{{ entity.entity_type.name }}</v-card-title>
    <v-card-text style="font-size: 18px">{{ entity.value }}</v-card-text>
    <v-divider></v-divider>
    <v-hover>
      <template v-slot:default="{ hover }">
        <v-card
          color="red lighten-5"
          outlined
          rounded="xl"
          class="d-flex align-center mx-4 mt-3 mb-3"
          :elevation="hover ? 2 : 0"
          @click="openSignalInstanceTab"
        >
          <v-card-text class="d-flex align-center">
            <v-progress-linear
              v-if="isLoading"
              height="3"
              color="red lighten-1"
              indeterminate
            ></v-progress-linear>
            <span v-else>
              <span v-if="signalInstanceCount > 1">
                Seen in
                <span v-bind:class="{ 'font-weight-bold': signalInstanceCount > 5 }">{{
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
      <template v-slot:default="{ hover }">
        <v-card
          color="red lighten-5"
          outlined
          rounded="xl"
          class="d-flex align-center mx-4 mt-3 mb-3"
          :elevation="hover ? 2 : 0"
          @click="createCaseShow(getCaseTable())"
        >
          <v-card-text class="d-flex align-center">
            <v-progress-linear
              v-if="isLoading"
              height="3"
              color="red lighten-1"
              indeterminate
            ></v-progress-linear>
            <span v-else>
              <span v-if="caseCount > 1">
                Seen in
                <span v-bind:class="{ 'font-weight-bold': caseCount > 5 }">{{ caseCount }}</span>
                other cases
              </span>
              <span v-else> First time this entity has been seen in a case </span>
            </span>
          </v-card-text>
        </v-card>
      </template>
    </v-hover>
    <v-dialog v-model="dialog" max-width="1080">
      <template v-slot:activator="{ on }"></template>
      <signal-instance-tab :inputSignalInstances="signalInstances" />
    </v-dialog>
    <v-dialog v-model="showCaseView" max-width="1080">
      <template v-slot:activator="{ on }"></template>
      <case-tab :inputCases="cases" />
    </v-dialog>
  </v-card>
</template>

<script>
import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import CaseApi from "@/case/api"
import CaseTab from "@/case/CaseTab.vue"
import EntityApi from "@/entity/api"
import SearchUtils from "@/search/utils"
import SignalInstanceTab from "@/signal/SignalInstanceTab.vue"

export default {
  name: "EntityCard",
  props: {
    entity: {
      type: Object,
      required: true,
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
    ...mapFields("route", ["query"]),
  },
  data() {
    return {
      caseCount: null,
      signalInstanceCount: null,
      isLoading: true,
      dialog: false,
      signalInstances: [],
      cases: [],
      filters: {
        entity: [],
        start: null,
        end: null,
      },
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
    ...mapActions("entity", ["createCaseShow"]),
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
        this.caseCount = casesResponse.cases.length
        this.signalInstanceCount = signalResponse.instances.length
        this.isLoading = false
      } catch (error) {
        console.error("Error in refreshData:", error)
      }
    },
    async getSignalInstances(selectedDateTime) {
      this.signalInstances = await EntityApi.getSignalInstances(
        this.entity.id,
        selectedDateTime
      ).then((response) => response.data.instances)
    },
    getCaseTable() {
      this.filters.entities = [this.entity]
      const startDate = this.getStartDate()
      const endDate = new Date()
      this.filters.start = [startDate]
      this.filters.end = [endDate]

      const expression = SearchUtils.createFilterExpression(this.filters)
      if (!expression) return

      const params = { filter: expression, itemsPerPage: 50 }

      return CaseApi.getAll(params)
        .then((response) => {
          this.cases = response.data.items
          return response.data.items
        })
        .catch((error) => {
          console.error(error)
        })
    },
    async openSignalInstanceTab() {
      await this.getSignalInstances(this.selectedDateTime)
      this.dialog = true
      this.$nextTick(() => {
        this.$refs.signalInstanceTab = this.signalInstances
      })
    },
    getStartDate() {
      return new Date(Date.now() - this.selectedDateTime * 86400000).toISOString()
    },
  },
}
</script>
