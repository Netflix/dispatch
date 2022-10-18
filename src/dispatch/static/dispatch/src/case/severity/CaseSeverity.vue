<template>
  <div class="pl-5">
    <div v-if="severity == 'Low'">
      <v-badge bordered color="green" dot left offset-x="-10" offset-y="12">
        {{ severity }}
      </v-badge>
    </div>
    <div v-else-if="severity == 'Moderate'">
      <v-badge bordered color="orange" dot left offset-x="-10" offset-y="12">
        {{ severity }}
      </v-badge>
    </div>
    <div v-else-if="severity == 'High'">
      <v-badge bordered color="red" dot left offset-x="-10" offset-y="12">
        {{ severity }}
      </v-badge>
    </div>
    <div v-else-if="severity == 'Critical'">
      <v-badge bordered color="purple" dot left offset-x="-10" offset-y="12">
        {{ severity }}
      </v-badge>
    </div>
    <div v-else>
      <v-badge bordered color="grey" dot left offset-x="-10" offset-y="12">
        {{ severity }}
      </v-badge>
    </div>
  </div>
</template>

<script>
export default {
  name: "CaseSeverity",

  props: {
    severity: {
      type: String,
      required: true,
    },
  },
}
</script>
