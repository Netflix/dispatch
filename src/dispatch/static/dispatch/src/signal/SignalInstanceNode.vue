<script setup lang="ts">
import { Position } from "@vue-flow/core"

defineProps<{
  label: string
  data: any
}>()

defineEmits(["openViewer"])

// TODO: (wshel) Future release
// function openViewer() {
//   emit("openViewer", props.data)
// }
</script>

<template>
  <div>
    <div>{{ label }}</div>
    <!-- <button @click="openViewer">Open Viewer</button> -->
    <Handle id="a" type="source" :position="Position.Right" />
  </div>
</template>
