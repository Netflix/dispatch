<template>
  <v-menu v-model="menu" origin="overlap">
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
          <template #prepend>
            <v-avatar color="teal">
              {{ initials(value.name) }}
            </v-avatar>
          </template>

          <v-list-item-title>{{ value.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ value.status }}</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              :to="{
                name: 'CaseTableEdit',
                params: { name: value.name },
              }"
            >
              <v-icon>mdi-arrow-right-bold-circle</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
      <v-list>
        <template
          v-if="value.assignee && value.assignee.individual && value.assignee.individual.email"
        >
          <v-list-item>
            <template #prepend>
              <v-icon>mdi-briefcase</v-icon>
            </template>

            <v-list-item-subtitle>{{ value.assignee.individual.email }}</v-list-item-subtitle>
          </v-list-item>
        </template>
        <v-list-item>
          <template #prepend>
            <v-icon>mdi-domain</v-icon>
          </template>

          <v-list-item-subtitle>{{ value.title }}</v-list-item-subtitle>
        </v-list-item>
        <template v-if="value.case_type && value.case_type.name">
          <v-list-item>
            <template #prepend>
              <v-icon>mdi-domain</v-icon>
            </template>

            <v-list-item-subtitle>{{ value.case_type.name }}</v-list-item-subtitle>
          </v-list-item>
        </template>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import { initials } from "@/filters"

export default {
  name: "CasePopover",

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
