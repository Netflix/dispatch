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
            <v-list-item-title class="dispatch-text-title">{{ option }}</v-list-item-title>
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

<style lang="scss" scoped>
@import "@/styles/index.scss";
</style>
