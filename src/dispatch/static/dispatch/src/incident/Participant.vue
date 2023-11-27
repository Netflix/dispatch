<template>
  <v-menu v-model="menu" location="top" origin="overlap">
    <template #activator="{ props }">
      <v-chip pill size="small" v-bind="props" v-if="local_participant.individual">
        <v-avatar color="teal" start>
          <span class="text-white">{{ initials(local_participant.individual.name) }}</span>
        </v-avatar>
        {{ local_participant.individual.name }}
      </v-chip>
    </template>
    <v-card width="300">
      <v-list theme="dark">
        <v-list-item v-if="local_participant.individual">
          <template #prepend>
            <v-avatar color="teal">
              {{ initials(local_participant.individual.name) }}
            </v-avatar>
          </template>

          <v-list-item-title>{{ local_participant.individual.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ local_participant.individual.email }}</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon="mdi-close-circle"
              variant="text"
              density="comfortable"
              @click="menu = false"
            />
          </template>
        </v-list-item>
      </v-list>
      <v-list>
        <v-list-item prepend-icon="mdi-briefcase">
          <v-list-item-subtitle>{{ local_participant.individual.email }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="local_participant.individual.company" prepend-icon="mdi-domain">
          <v-list-item-subtitle>{{ local_participant.individual.company }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="local_participant.location" prepend-icon="mdi-earth">
          <v-list-item-subtitle>{{ local_participant.location }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="local_participant.department" prepend-icon="mdi-account-group">
          <v-list-item-subtitle>{{ local_participant.department }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="local_participant.team" prepend-icon="mdi-account-multiple">
          <v-list-item-subtitle>{{ local_participant.team }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item
          v-if="local_participant.individual.weblink"
          :href="local_participant.individual.weblink"
          target="_blank"
          prepend-icon="mdi-open-in-new"
        >
          <v-list-item-subtitle>External Profile</v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "IncidentParticipant",

  data: () => ({
    menu: false,
    local_participant: { individual: {} },
  }),

  setup() {
    return { initials }
  },

  props: {
    participant: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  created: function () {
    if (this.participant?.individual) {
      this.local_participant = this.participant
    }
  },
}
</script>
