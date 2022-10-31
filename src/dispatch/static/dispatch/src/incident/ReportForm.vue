<template>
  <v-app>
    <notification-snackbars-wrapper />

    <v-main>
      <v-app-bar app flat style="border-bottom: 1px solid #d2d2d2 !important" color="background0">
        <router-link :to="{ name: 'IncidentOverview' }" style="text-decoration: none">
          <span class="button font-weight-bold">D I S P A T C H</span>
        </router-link>
        <v-spacer />
        <v-btn small color="info" :to="{ name: 'status' }"> Active Incidents </v-btn>
      </v-app-bar>
      <organization-banner />
      <report-receipt-card v-if="id" />
      <report-submission-card v-else />
    </v-main>
  </v-app>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import NotificationSnackbarsWrapper from "@/components/NotificationSnackbarsWrapper.vue"
import ReportSubmissionCard from "@/incident/ReportSubmissionCard.vue"
import ReportReceiptCard from "@/incident/ReportReceiptCard.vue"
import OrganizationBanner from "@/organization/OrganizationBanner.vue"

export default {
  name: "ReportForm",

  props: {
    project: {
      type: String,
      default: null,
    },
  },

  components: {
    ReportSubmissionCard,
    ReportReceiptCard,
    OrganizationBanner,
    NotificationSnackbarsWrapper,
  },
  data() {
    return {}
  },
  computed: {
    ...mapFields("incident", ["selected.id"]),
  },
}
</script>
