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
            <v-list-item-avatar color="teal">
              <span class="text-white">{{ initials(participant.individual.name) }}</span>
            </v-list-item-avatar>

            <v-list-item-title>{{ participant.individual.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>

            <v-list-item-action>
              <v-btn icon variant="text" @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
        <v-list>
          <v-list-item>
            <v-list-item-action>
              <v-icon>mdi-briefcase</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ participant.individual.email }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.individual.company">
            <v-list-item-action>
              <v-icon>business</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ participant.individual.company }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.location">
            <v-list-item-action>
              <v-icon>public</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ participant.location }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.department">
            <v-list-item-action>
              <v-icon>groups</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ participant.department }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="participant.team">
            <v-list-item-action>
              <v-icon>group</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ participant.team }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item
            v-if="participant.individual.weblink"
            :href="participant.individual.weblink"
            target="_blank"
          >
            <v-list-item-action>
              <v-icon>open_in_new</v-icon>
            </v-list-item-action>
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
