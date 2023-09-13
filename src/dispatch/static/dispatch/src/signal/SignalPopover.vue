<template>
  <div>
    <v-menu v-model="menu" location="bottom right" transition="scale-transition" origin="top left">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props">
          <v-avatar color="teal" start>
            <span class="text-white">{{ initials(value.name) }}</span>
          </v-avatar>
          {{ value.name }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <v-list-item-avatar color="teal">
              <span class="text-white">{{ initials(value.name) }}</span>
            </v-list-item-avatar>

            <v-list-item-title>{{ value.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ value.variant }}</v-list-item-subtitle>

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
            <v-list-item-subtitle>{{ value.owner }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-action>
              <v-icon>business</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ value.description }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="value.external_url" :href="value.external_url" target="_blank">
            <v-list-item-action>
              <v-icon>open_in_new</v-icon>
            </v-list-item-action>
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
