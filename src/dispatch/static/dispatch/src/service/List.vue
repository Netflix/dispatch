<template>
  <v-list v-if="items.length">
    <v-list-group prepend-icon="room_service" no-action color="primary">
      <template v-slot:activator>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>Services ({{ items.length }})</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </template>
      <v-list-item v-for="item in items" :key="item.content.id" @click="">
        <v-list-item-content>
          <v-list-item-title v-text="item.content.name"></v-list-item-title>
          <v-list-item-subtitle>Name</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list-group>
  </v-list>
</template>
<script>
export default {
  name: "ServiceList",
  props: {
    items: {
      default: null,
      type: Array
    }
  }
}
</script>
