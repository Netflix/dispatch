<template>
  <div>
    <v-menu v-model="menu" location="bottom right" transition="scale-transition" origin="top left">
      <template #activator="{ on }">
        <v-chip pill small v-on="on">
          <v-avatar color="teal" start>
            <span class="text-white">{{ service.name | initials }}</span>
          </v-avatar>
          {{ service.name }}
        </v-chip>
      </template>
      <v-card width="300">
        <v-list dark>
          <v-list-item>
            <v-list-item-avatar color="teal">
              <span class="text-white">{{ service.name | initials }}</span>
            </v-list-item-avatar>

            <v-list-item-title>{{ service.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ service.type }}</v-list-item-subtitle>

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
              <v-icon>mdi-information</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>{{ service.description }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-action>
              <v-icon>mdi-toggle-switch</v-icon>
            </v-list-item-action>
            <v-list-item-subtitle>
              <span v-if="service.is_active">Active</span><span v-else>Inactive</span>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "ServicePopover",

  data: () => ({
    menu: false,
  }),

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
