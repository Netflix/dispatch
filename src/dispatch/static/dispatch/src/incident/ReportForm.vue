<template>
  <v-app>
    <v-content>
      <v-app-bar app flat class="v-bar--underline" color="white">
        <router-link to="/" tag="span">
          <span class="button font-weight-bold">D I S P A T C H</span>
        </router-link>
        <v-spacer />
        <v-btn small color="info" to="/incidents/status">
          Active Incidents
        </v-btn>
      </v-app-bar>
      <report-receipt-card v-if="id" />
      <report-submission-card v-else />
    </v-content>
  </v-app>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import ReportSubmissionCard from "@/incident/ReportSubmissionCard.vue"
import ReportReceiptCard from "@/incident/ReportReceiptCard.vue"
export default {
  name: "ReportForm",

  components: {
    ReportSubmissionCard,
    ReportReceiptCard
  },
  data() {
    return {}
  },
  computed: {
    ...mapFields("incident", ["selected.id"])
  }
}
</script>
