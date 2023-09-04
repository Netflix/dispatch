<template>
  <div class="pl-5">
    <div v-if="priority == 'Low'">
      <v-badge bordered color="info" dot location="left" offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
    <div v-else-if="priority == 'Medium'">
      <v-badge bordered color="warning" dot location="left" offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
    <div v-else-if="priority == 'High'">
      <v-badge bordered color="error" dot location="left" offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
    <div v-else>
      <v-badge bordered color="error" dot location="left" offset-x="-10" offset-y="12">
        {{ priority }}
      </v-badge>
    </div>
  </div>
</template>

<script>
export default {
  name: "IncidentPriority",

  props: {
    priority: {
      type: String,
      required: true,
    },
  },
}
</script>
