<template>
  <div>
    <v-menu v-model="menu" bottom right transition="scale-transition" origin="top left">
      <template v-slot:activator="{ on }">
        <v-chip pill small v-on="on">
          <v-avatar color="teal" left>
            <span class="white--text">{{ value.name | initials }}</span>
          </v-avatar>
          {{ value.name }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <v-list-item-avatar color="teal">
              <span class="white--text">{{ value.name | initials }}</span>
            </v-list-item-avatar>
            <v-list-item-content>
              <v-list-item-title>{{ value.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ value.status }}</v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
        <v-list>
          <template
            v-if="value.assignee && value.assignee.individual && value.assignee.individual.email"
          >
            <v-list-item>
              <v-list-item-action>
                <v-icon>mdi-briefcase</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ value.assignee.individual.email }}</v-list-item-subtitle>
            </v-list-item>
          </template>
          <v-list-item>
            <v-list-item-action>
              <v-icon>business</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ value.title }}</v-list-item-subtitle>
          </v-list-item>
          <template v-if="value.case_type && value.case_type.name">
            <v-list-item>
              <v-list-item-action>
                <v-icon>business</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ value.case_type.name }}</v-list-item-subtitle>
            </v-list-item>
          </template>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "CasePopover",

  data: () => ({
    menu: false,
  }),

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
