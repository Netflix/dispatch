<script setup lang="ts">
import { defineProps } from "vue"
import Hotkey from "@/atomics/Hotkey.vue"

// Define the Anchor type
type Anchor = "top" | "bottom" | "start" | "end" | "left" | "right" | "center"

/* Define component props
 * text: a string that represents the tooltip text
 * hotkeys: an array of strings, each representing a hotkey to display
 */
const props = withDefaults(
  defineProps<{
    text: string
    hotkeys: string[]
    location?: Anchor
  }>(),
  {
    location: "bottom",
  }
)
</script>

<!--
 * Usage Example:
 *
 * <Tooltip text="Save changes" :hotkeys="['Ctrl', 'S']">
 *   <template v-slot:activator="{ tooltip }">
 *     <v-btn v-bind="tooltip">Save</v-btn>
 *   </template>
 * </Tooltip>
 *
 * This example creates a Tooltip with the text "Save changes" and hotkeys "Ctrl + S".
 * The tooltip is activated by a button with the text "Save".
 */
 -->

<template>
  <!-- This is a tooltip component that displays text and hotkeys. -->
  <v-tooltip :location="props.location" open-delay="750" transition="fade-transition">
    <template #activator="{ props: tooltip }">
      <!-- Tooltip activator slot. Pass the activator component here. -->
      <slot name="activator" :tooltip="tooltip" />
    </template>

    <v-row no-gutters>
      <!-- Tooltip text -->
      <v-col align-self="start">
        <span>{{ text }}</span>
      </v-col>

      <!-- Hotkeys display -->
      <v-col align-self="end" :cols="hotkeys.length" v-if="hotkeys.length">
        <Hotkey v-for="(hotkey, index) in hotkeys" :key="index" :hotkey="hotkey" />
      </v-col>
    </v-row>
  </v-tooltip>
</template>

<style scoped>
.v-tooltip :deep(.v-overlay__content) {
  align-items: center !important;
  max-height: 30px !important;
  opacity: 2 !important;
  color: rgb(25, 28, 24) !important;
  font-size: 0.6875rem !important;
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  background-color: rgba(255, 255, 255, 0.5) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
}
</style>
