<template>
  <v-badge class="pl-5" bordered :color="color" dot location="left" offset-x="-16">
    {{ priority }}
  </v-badge>
</template>

<script>
export default {
  name: "IncidentPriority",

  props: {
    priority: {
      type: String,
      required: true,
    },
    color: {
      type: String,
      default: "info",
    },
  },
}
</script>
