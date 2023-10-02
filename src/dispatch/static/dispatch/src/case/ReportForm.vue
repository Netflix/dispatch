<template>
  <v-app>
    <notification-snackbars-wrapper />
    <v-main>
      <v-app-bar flat style="border-bottom: 1px solid #d2d2d2 !important" color="background0">
        <template #prepend>
          <router-link :to="{ name: 'CaseOverview' }" style="text-decoration: none">
            <span class="button font-weight-bold">D I S P A T C H</span>
          </router-link>
        </template>
        <template #append>
          <v-btn size="small" color="info" :to="{ name: 'caseStatus' }"> Active Issues </v-btn>
        </template>
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
import ReportSubmissionCard from "@/case/ReportSubmissionCard.vue"
import ReportReceiptCard from "@/case/ReportReceiptCard.vue"
import OrganizationBanner from "@/organization/OrganizationBanner.vue"

export default {
  name: "CaseReportForm",

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
    ...mapFields("case_management", ["selected.id"]),
  },
}
</script>
