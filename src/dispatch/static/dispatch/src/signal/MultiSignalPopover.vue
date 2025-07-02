<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props"> {{ signals.length }} Signals </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <v-list-item-title>{{ signals.length }} Signals</v-list-item-title>

            <template #append>
              <v-btn icon variant="text" @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </template>
          </v-list-item>
        </v-list>
        <v-list>
          <v-list-item v-for="(signal, index) in signals" :key="index">
            <template #prepend>
              <v-avatar color="teal" size="small">
                {{ initials(signal.name) }}
              </v-avatar>
            </template>

            <v-list-item-title>{{ signal.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ signal.variant }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider v-if="signals.length > 0" />
          <v-list-item v-if="commonOwner">
            <template #prepend>
              <v-icon>mdi-briefcase</v-icon>
            </template>
            <v-list-item-subtitle>{{ commonOwner }}</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "MultiSignalPopover",

  data: () => ({
    menu: false,
  }),

  setup() {
    return { initials }
  },

  props: {
    signals: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  computed: {
    commonOwner() {
      // Check if all signals have the same owner
      if (this.signals.length === 0) return null

      const firstOwner = this.signals[0].owner
      const allSameOwner = this.signals.every((signal) => signal.owner === firstOwner)

      return allSameOwner ? firstOwner : "Multiple Owners"
    },
  },
}
</script>
