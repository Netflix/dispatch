<style>
.info-widget .v-alert__border {
  position: absolute;
  top: 6px;
  bottom: 6px;
  left: 1px;
  width: 5px;
  opacity: 0.5 !important;
  border-radius: 0px 3px 3px 0px;
  border: none;
  transition: background-color 0.15s linear 0s;
  background: currentColor;
}
</style>

<template>
  <v-alert variant="text" border="start" color="info" class="info-widget">
    <span class="on-surface text-subtitle-1">{{ text }}</span>
  </v-alert>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      default: "",
    },
  },
}
</script>
