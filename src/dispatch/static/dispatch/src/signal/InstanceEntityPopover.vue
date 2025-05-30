<template>
  <div>
    <v-menu v-model="menu" origin="overlap">
      <template #activator="{ props }">
        <v-chip v-bind="props">
          {{ value.length }} <v-icon class="pl-2">mdi-cube-outline</v-icon>
        </v-chip>
      </template>
      <v-card v-if="value.length > 0" max-width="600px" class="pb-4">
        <v-list-dark v-bind="props">
          <v-list-item>
            <v-list-item-title>Entities</v-list-item-title>
            <template #append>
              <v-btn icon variant="text" @click="menu = false">
                <v-icon>mdi-close-circle</v-icon>
              </v-btn>
            </template>
          </v-list-item>
          <v-list-item v-for="entity in value" :key="`${entity.entity_type.name}-${entity.value}`">
            <h5>{{ entity.entity_type.name }}</h5>
            {{ entity.value }}
          </v-list-item>
        </v-list-dark>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  name: "InstanceEntityPopover",

  data: () => ({
    menu: false,
  }),

  setup() {},

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
