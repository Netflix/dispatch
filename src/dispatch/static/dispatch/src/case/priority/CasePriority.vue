<template>
  <v-badge class="pl-5" bordered :color="color" dot location="left" offset-x="-16">
    {{ priority }}
  </v-badge>
</template>

<script>
export default {
  name: "CasePriority",

  props: {
    priority: {
      type: String,
      required: true,
    },
  },

  computed: {
    color() {
      return (
        {
          Low: "green",
          Medium: "orange",
          High: "red",
        }[this.priority] || "red"
      )
    },
  },
}
</script>
