<script setup lang="ts">
import { Position } from "@vue-flow/core"

const props = defineProps<{
  label: string
  data: any
}>()

const emit = defineEmits(["openViewer"])

function openViewer() {
  emit("openViewer", props.data)
}
</script>

<template>
  <div>
    <div>{{ label }}</div>
    <button @click="openViewer">Open Viewer</button>
    <Handle id="a" type="source" :position="Position.Right" />
  </div>
</template>
