<template>
  <div class="pl-5">
    <div v-if="priority == 'Low'">
      <v-badge bordered color="green" dot left offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
    <div v-else-if="priority == 'Medium'">
      <v-badge bordered color="orange" dot left offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
    <div v-else-if="priority == 'High'">
      <v-badge bordered color="red" dot left offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
    <div v-else>
      <v-badge bordered color="red" dot left offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
  </div>
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
}
</script>
