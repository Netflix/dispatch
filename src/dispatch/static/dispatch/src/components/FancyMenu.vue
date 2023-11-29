<template>
  <div>
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      location="start"
      offset="10"
      transition="false"
    >
      <template v-slot:activator="{ props: menu }">
        <v-btn class="text-subtitle-2 font-weight-regular" variant="text" v-bind="menu">
          <v-icon>mdi-dots-horizontal</v-icon>
        </v-btn>
      </template>

      <v-card min-width="200" class="rounded-lg dispatch-side-card">
        <v-divider></v-divider>
        <v-list lines="one">
          <v-list-item
            v-for="(option, index) in options"
            :key="index"
            @click="selectOption(option)"
            density="compact"
            rounded="lg"
            active-class="ma-4"
          >
            <v-list-item-title class="item-title-font">{{ option }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import type { Ref } from "vue"

const props = defineProps<{ options: string[] }>()

const menu: Ref<boolean> = ref(false)

const emit = defineEmits(["selection-changed"])

const selectOption = (option: string) => {
  emit("selection-changed", option)
  menu.value = false
}
</script>

<style scoped>
.dispatch-side-card {
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 8px !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 3px 12px !important;
  color: rgb(60, 65, 73) !important;
  opacity: 2 !important;
}

.item-title-font {
  font-size: 13px !important;
}
</style>
