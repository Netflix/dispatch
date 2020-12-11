<template>
  <div class="pl-5">
    <div v-if="status == 'Active'">
      <v-badge bordered color="error" dot left offset-x="-10" offset-y="12">
        {{ status }}
      </v-badge>
    </div>
    <div v-if="status == 'Stable'">
      <v-badge bordered color="warning" dot left offset-x="-10" offset-y="12">
        {{ status }}
      </v-badge>
    </div>
    <div v-if="status == 'Closed'">
      <v-badge bordered color="success" dot left offset-x="-10" offset-y="12">
        {{ status }}
      </v-badge>
    </div>
  </div>
</template>

<script>
export default {
  name: "IncidentStatus",

  props: {
    status: {
      type: String,
      required: true
    }
  }
}
</script>
