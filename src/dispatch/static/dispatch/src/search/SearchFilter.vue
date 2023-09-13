<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip pill size="small" v-bind="props">
          <v-avatar color="teal" start>
            <span class="text-white">{{ initials(filter.name) }}</span>
          </v-avatar>
          {{ filter.name }}
        </v-chip>
      </template>
      <v-card width="400">
        <v-list dark>
          <v-list-item>
            <v-list-item-avatar color="teal">
              <span class="text-white">{{ initials(filter.name) }}</span>
            </v-list-item-avatar>

            <v-list-item-title>{{ filter.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ filter.type }}</v-list-item-subtitle>

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
              <v-icon>mdi-text-box</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ filter.description }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="filter.expression">
            <v-list-item-action>
              <v-icon>mdi-code-json</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>
              <pre>{{ filter.expression }}</pre>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "SearchFilter",

  data: () => ({
    menu: false,
  }),

  setup() {
    return { initials }
  },

  props: {
    filter: {
      type: Object,
      default: null,
    },
  },
}
</script>
