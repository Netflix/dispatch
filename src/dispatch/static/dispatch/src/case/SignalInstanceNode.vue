<script setup>
import { Handle, Position } from "@vue-flow/core"
import { ref, defineEmits } from "vue"

const props = defineProps(["label", "data"])

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
