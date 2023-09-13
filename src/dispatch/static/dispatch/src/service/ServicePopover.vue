<template>
  <v-menu v-model="menu" location="top" origin="overlap">
    <template #activator="{ props }">
      <v-chip pill size="small" v-bind="props">
        <v-avatar color="teal" start>
          {{ initials(service.name) }}
        </v-avatar>
        {{ service.name }}
      </v-chip>
    </template>
    <v-card width="300">
      <v-list theme="dark">
        <v-list-item>
          <template #prepend>
            <v-avatar color="teal">
              {{ initials(service.name) }}
            </v-avatar>
          </template>

          <v-list-item-title>{{ service.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ service.type }}</v-list-item-subtitle>

          <template #append>
            <v-btn icon="mdi-close-circle" variant="text" @click="menu = false" />
          </template>
        </v-list-item>
      </v-list>
      <v-list>
        <v-list-item prepend-icon="mdi-information">
          <v-list-item-subtitle>{{ service.description }}</v-list-item-subtitle>
        </v-list-item>
        <v-list-item prepend-icon="mdi-toggle-switch">
          <v-list-item-subtitle v-if="service.is_active">Active</v-list-item-subtitle>
          <v-list-item-subtitle v-else>Inactive</v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "ServicePopover",

  data: () => ({
    menu: false,
  }),

  setup() {
    return { initials }
  },

  props: {
    service: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },
}
</script>
