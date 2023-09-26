<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props" v-if="participant.individual">
          <v-avatar color="teal" start>
            <span class="text-white">{{ initials(participant.individual.name) }}</span>
          </v-avatar>
          {{ participant.individual.name }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item v-if="participant.individual">
            <template #prepend>
              <v-avatar color="teal">
                <span class="text-white">{{ initials(participant.individual.name) }}</span>
              </v-avatar>
            </template>

            <v-list-item-title>{{ participant.individual.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>

            <template #append>
              <v-btn icon variant="text" @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </template>
          </v-list-item>
        </v-list>
        <v-list>
          <v-list-item>
            <template #prepend>
              <v-icon>mdi-briefcase</v-icon>
            </template>

            <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.individual.company">
            <template #prepend>
              <v-icon>business</v-icon>
            </template>

            <v-list-item-subtitle>{{ participant.individual.company }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.location">
            <template #prepend>
              <v-icon>public</v-icon>
            </template>

            <v-list-item-subtitle>{{ participant.location }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.department">
            <template #prepend>
              <v-icon>groups</v-icon>
            </template>

            <v-list-item-subtitle>{{ participant.department }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.team">
            <template #prepend>
              <v-icon>group</v-icon>
            </template>

            <v-list-item-subtitle>{{ participant.team }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item
            v-if="participant.individual.weblink"
            :href="participant.individual.weblink"
            target="_blank"
          >
            <template #prepend>
              <v-icon>mdi-open-in-new</v-icon>
            </template>

            <v-list-item-subtitle>External Profile</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "CaseParticipant",

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
