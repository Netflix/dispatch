<template>
  <div class="text-no-wrap">
    <v-badge bordered :color="color" dot location="left" offset-x="-16">
      {{ status }}
    </v-badge>
    <template v-if="status !== 'Closed' && dedicatedChannel">
      <v-tooltip location="bottom" text="Join" v-if="allowSelfJoin && visibility !== 'Restricted'">
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            icon="mdi-account-plus"
            variant="text"
            density="comfortable"
            class="ml-1"
            @click.stop="joinCase(id)"
          />
        </template>
      </v-tooltip>
    </template>
    <template v-if="incidents && incidents.length > 0">
      <v-tooltip location="bottom" :text="`View incident`">
        <template #activator="{ props }">
          <v-btn
            v-bind="props"
            icon="mdi-fire"
            variant="text"
            density="comfortable"
            class="ml-1"
            color="orange"
            @click.stop="navigateToIncident(incidents[0])"
          />
        </template>
      </v-tooltip>
    </template>
  </div>
</template>

<script>
import { mapActions } from "vuex"

export default {
  name: "CaseStatus",

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
    dedicatedChannel: {
      type: Boolean,
      required: true,
    },
    visibility: {
      type: String,
      required: false,
      default: "Open",
    },
    incidents: {
      type: Array,
      default: () => [],
    },
  },

  computed: {
    color() {
      return (
        {
          New: "red",
          Triage: "orange",
          Escalated: "yellow",
          Stable: "blue",
          Closed: "success",
        }[this.status] || "error"
      )
    },
  },

  methods: {
    ...mapActions("case_management", ["joinCase"]),
    navigateToIncident(incident) {
      this.$router.push({
        name: "IncidentTableEdit",
        params: { name: incident.name },
      })
    },
  },
}
</script>
