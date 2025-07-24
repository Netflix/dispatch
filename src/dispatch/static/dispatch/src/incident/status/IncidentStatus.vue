<template>
  <div class="text-no-wrap">
    <v-badge bordered :color="badgeColor" dot location="left" offset-x="-16">
      {{ status }}
    </v-badge>
    <template v-if="status === 'Active' || status === 'Stable'">
      <v-tooltip location="bottom" text="Join" v-if="allowSelfJoin">
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            icon="mdi-account-plus"
            variant="text"
            density="comfortable"
            class="ml-1"
            @click.stop="joinIncident(id)"
          />
        </template>
      </v-tooltip>
      <v-tooltip location="bottom" text="Subscribe">
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            icon="mdi-email-plus"
            variant="text"
            density="comfortable"
            @click.stop="subscribeToIncident(id)"
          />
        </template>
      </v-tooltip>
    </template>
    <template v-if="cases && cases.length > 0">
      <v-tooltip location="bottom" :text="`View case`">
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            icon="mdi-briefcase"
            variant="text"
            density="comfortable"
            class="ml-1"
            color="blue"
            @click.stop="navigateToCase(cases[0])"
          />
        </template>
      </v-tooltip>
    </template>
  </div>
</template>

<script>
import { mapActions } from "vuex"

export default {
  name: "IncidentStatus",

  props: {
    status: {
      type: String,
      required: true,
    },
    id: {
      type: Number,
      required: true,
    },
    allowSelfJoin: {
      type: Boolean,
      required: true,
    },
    cases: {
      type: Array,
      default: () => [],
    },
  },

  computed: {
    badgeColor() {
      return (
        {
          Active: "error",
          Stable: "warning",
          Closed: "success",
        }[this.status] || "error"
      )
    },
  },

  methods: {
    ...mapActions("incident", ["joinIncident", "subscribeToIncident"]),
    navigateToCase(caseItem) {
      this.$router.push({
        name: "CaseTableEdit",
        params: { name: caseItem.name },
      })
    },
  },
}
</script>
