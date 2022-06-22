<template>
  <div>
    <div v-if="status == 'Active'">
      <v-badge bordered color="error" slot="activator" dot left offset-x="-10" offset-y="12">
        {{ status }}
      </v-badge>
    </div>
    <div v-if="status == 'Stable'">
      <v-badge bordered color="warning" slot="activator" dot left offset-x="-10" offset-y="12">
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
}
</script>
