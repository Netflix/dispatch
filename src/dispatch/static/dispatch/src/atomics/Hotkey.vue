<script setup lang="ts">
const { hotkey } = defineProps<{ hotkey: string }>()
</script>

<template>
  <span class="hotkey">{{ hotkey }}</span>
</template>

<style scoped>
.hotkey {
  vertical-align: baseline;
  text-transform: capitalize;
  text-align: center;
  color: rgba(0, 0, 0, 0.816);
  font-size: 11px;
  line-height: 110%;
  border-radius: 4px;
  padding-left: 4px;
  padding-right: 4px;
  padding-top: 1px;
  min-width: 17px;
  border: 0.5px solid rgb(216, 216, 216);
  background-color: rgb(254, 255, 254);
  box-shadow: rgba(0, 0, 0, 0.086) 0px 2px 0px 0px;
}
</style>
