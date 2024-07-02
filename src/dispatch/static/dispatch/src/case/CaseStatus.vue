<template>
  <div class="text-no-wrap">
    <v-badge bordered :color="color" dot location="left" offset-x="-16">
      {{ status }}
    </v-badge>
    <template v-if="status !== 'Closed' && dedicatedChannel">
      <v-tooltip location="bottom" text="Join" v-if="allowSelfJoin">
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
  },

  computed: {
    color() {
      return (
        {
          New: "red",
          Triage: "orange",
          Escalated: "yellow",
          Closed: "success",
        }[this.status] || "error"
      )
    },
  },

  methods: {
    ...mapActions("case_management", ["joinCase"]),
  },
}
</script>
