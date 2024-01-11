<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props">
          <template #prepend>
            <v-avatar color="teal" start>
              {{ initials(value.name) }}
            </v-avatar>
          </template>
          {{ value.name }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <template #prepend>
              <v-avatar color="teal">
                {{ initials(value.name) }}
              </v-avatar>
            </template>

            <v-list-item-title>{{ value.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ value.variant }}</v-list-item-subtitle>

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

            <v-list-item-subtitle>{{ value.owner }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <template #prepend>
              <v-icon>mdi-domain</v-icon>
            </template>

            <v-list-item-subtitle>{{ value.description }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.external_url" :href="value.external_url" target="_blank">
            <template #prepend>
              <v-icon>mdi-open-in-new</v-icon>
            </template>

            <v-list-item-subtitle>External Documentation</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "SignalPopover",

  data: () => ({
    menu: false,
  }),

  setup() {
    return { initials }
  },

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },
}
</script>
