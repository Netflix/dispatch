<template>
  <v-card class="widget-card" outlined elevation="0">
    <v-card-text class="pa-0">
      <div class="subtitle pt-6 pl-6">{{ subTitle }}</div>
    </v-card-text>
    <v-card-title class="pl-6">
      {{ title }}
      <v-spacer></v-spacer>
      <v-chip small outlined><v-icon x-small class="pr-2">mdi-arrow-up-thick</v-icon>24%</v-chip>
    </v-card-title>
  </v-card>
</template>

<script>
export default {
  name: "CaseStatWidget",
  props: {
    supTitle: {
      type: String,
      default: "",
    },
    subTitle: {
      type: String,
      default: "Open Cases",
    },
    title: {
      type: [Number, String],
      default: "",
    },
    icon: {
      type: String,
      default: "",
    },
    color: {
      type: String,
      default: "",
    },
  },

  data() {
    return {}
  },
}
</script>
