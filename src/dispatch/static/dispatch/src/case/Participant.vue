<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props" v-if="local_participant.individual">
          <v-avatar color="teal" start>
            <span class="text-white">{{ initials(local_participant.individual.name) }}</span>
          </v-avatar>
          {{ local_participant.individual.name }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item v-if="local_participant.individual">
            <template #prepend>
              <v-avatar color="teal">
                <span class="text-white">{{ initials(local_participant.individual.name) }}</span>
              </v-avatar>
            </template>

            <v-list-item-title>{{ local_participant.individual.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ local_participant.individual.email }}</v-list-item-subtitle>

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

            <v-list-item-subtitle>{{ local_participant.individual.email }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="local_participant.individual.company">
            <template #prepend>
              <v-icon>mdi-domain</v-icon>
            </template>

            <v-list-item-subtitle>{{ local_participant.individual.company }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="local_participant.location">
            <template #prepend>
              <v-icon>mdi-earth</v-icon>
            </template>

            <v-list-item-subtitle>{{ local_participant.location }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="local_participant.department">
            <template #prepend>
              <v-icon>mdi-account-group-outline</v-icon>
            </template>

            <v-list-item-subtitle>{{ local_participant.department }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="local_participant.team">
            <template #prepend>
              <v-icon>mdi-account-multiple-outline</v-icon>
            </template>

            <v-list-item-subtitle>{{ local_participant.team }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item
            v-if="local_participant.individual.weblink"
            :href="local_participant.individual.weblink"
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
