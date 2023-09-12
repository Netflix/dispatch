<template>
  <v-menu v-model="menu" location="top left" origin="overlap">
    <template #activator="{ props }">
      <v-chip pill size="small" v-bind="props" v-if="participant.individual">
        <v-avatar color="teal" start>
          <span class="text-white">{{ initials(participant.individual.name) }}</span>
        </v-avatar>
        {{ participant.individual.name }}
      </v-chip>
    </template>
    <v-card width="300">
      <v-list theme="dark">
        <v-list-item v-if="participant.individual">
          <template #prepend>
            <v-avatar color="teal">
              {{ initials(participant.individual.name) }}
            </v-avatar>
          </template>

          <v-list-item-title>{{ participant.individual.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>

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
          <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="participant.individual.company" prepend-icon="mdi-domain">
          <v-list-item-subtitle>{{ participant.individual.company }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="participant.location" prepend-icon="mdi-earth">
          <v-list-item-subtitle>{{ participant.location }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="participant.department" prepend-icon="mdi-account-group">
          <v-list-item-subtitle>{{ participant.department }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="participant.team" prepend-icon="mdi-account-multiple">
          <v-list-item-subtitle>{{ participant.team }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item
          v-if="participant.individual.weblink"
          :href="participant.individual.weblink"
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
}
</script>
