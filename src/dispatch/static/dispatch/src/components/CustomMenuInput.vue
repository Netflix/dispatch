<template>
  <v-input :model-value="value" @click="menu = !menu" readonly append-icon="mdi-menu-down">
    <template #prepend>
      <!-- Icon and label here-->
    </template>

    <template #append>
      <v-menu v-model="menu" :close-on-content-click="false">
        <template #activator="{ props }">
          <v-icon v-bind="props">mdi-menu-down</v-icon>
        </template>
        <v-list>
          <v-list-item v-for="(item, index) in items" :key="index" @click="selectItem(item)">
            <v-list-item-title>
              {{ item.text }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-input>
</template>

<script>
import { ref } from "vue"

export default {
  name: "CustomMenuInput",
  props: {
    items: Array,
    value: [String, Number],
  },
  setup(props, { emit }) {
    const menu = ref(false)

    const selectItem = (item) => {
      emit("update:value", item.value)
      menu.value = false
    }

    return { menu, selectItem }
  },
}
</script>

<style scoped>
.v-input {
}

.v-menu {
}
</style>
