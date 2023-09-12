<template>
  <v-badge bordered :color="color" dot location="left" offset-x="-16">
    {{ status }}
  </v-badge>
</template>

<script>
export default {
  name: "CaseStatus",

  props: {
    status: {
      type: String,
      required: true,
    },
    id: {
      type: Number,
      required: true,
    },
  },

  computed: {
    color() {
      return (
        {
          New: "red",
          Triage: "orange",
          Escalated: "yellow",
          Closed: "success",
        }[this.status] || "error"
      )
    },
  },
}
</script>
