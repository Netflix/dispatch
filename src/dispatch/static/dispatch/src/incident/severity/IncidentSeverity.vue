<template>
  <div class="pl-5">
    <div>
      <v-badge bordered :color="color" dot location="left" offset-x="-10" offset-y="12">
        {{ severity }}
      </v-badge>
    </div>
  </div>
</template>

<script>
export default {
  name: "IncidentSeverity",

  props: {
    severity: {
      type: String,
      required: true,
    },

    color: {
      type: String,
      default: "grey",
    },
  },
}
</script>
