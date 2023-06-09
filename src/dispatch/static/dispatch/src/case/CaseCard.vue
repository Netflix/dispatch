<template>
  <v-card elevation="0.9" outlined class="position-relative rounded-lg" height="300" width="450">
    <v-card-subtitle class="grey lighten-5 text--darken-5">
      <b>{{ _case.name }}</b> {{ _case.title }}
    </v-card-subtitle>
    <v-divider></v-divider>
    <v-card-text class="mt-1 mb-1">
      <v-row align="center" class="mx-0">
        <div class="pr-2">
          <v-icon dense :color="getPriorityColor(_case.case_priority)">
            mdi-alert-plus-outline
          </v-icon>
          {{ _case.case_priority && _case.case_priority.name ? _case.case_priority.name : "N/A" }}
        </div>
        <div class="pr-2">
          <v-icon dense> mdi-clock-time-seven-outline </v-icon>
          {{ _case.created_at | formatRelativeDate }}
        </div>

        <div class="grey--text">
          <v-icon dense color="grey lighten-1"> mdi-shape </v-icon>
          {{ _case.case_type && _case.case_type.name ? _case.case_type.name : "N/A" }}
        </div>
      </v-row>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-text>
      <div>{{ _case.description }}</div>
      <v-row align="center" class="pt-8 pb-2">
        <div class="pl-2">
          <v-icon dense color="grey lighten-1"> mdi-badge-account-outline </v-icon
          >{{ _case.assignee ? _case.assignee.individual.name : "N/A" }}
        </div>
        <v-btn
          class="pr-6 ml-auto no-hover-effect"
          text
          plain
          small
          depressed
          @click="openEditSheet(_case)"
        >
          <v-icon dense color="grey lighten-1"> mdi-file-find </v-icon>View
        </v-btn>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "CaseCardFinished",
  props: {
    _case: {
      type: Object,
      required: false,
      default: () => ({}), // returns an empty object if _case is not provided
    },
  },
  methods: {
    openEditSheet(item) {
      this.$router.push({ name: "CasePage", params: { name: item.name, _case: item } })
    },
    getPriorityColor(priority) {
      if (priority) {
        switch (priority.name) {
          case "Low":
            return "green lighten-1"
          case "Medium":
            return "orange"
          case "High":
            return "red darken-2"
          case "Critical":
            return "red darken-4"
        }
      }
      return "red darken-2"
    },
  },
}
</script>

<style scoped>
.no-hover-effect {
  text-transform: none;
}

.no-hover-effect:hover {
  background-color: transparent !important;
}
</style>
