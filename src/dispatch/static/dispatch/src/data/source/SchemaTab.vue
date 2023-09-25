<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-card>
          <v-list-item lines="two">
            <v-list-item-title class="text-h5"> Example Log </v-list-item-title>
          </v-list-item>
          <v-list-item>
            <pre> {{ example_log }} </pre>
          </v-list-item>
        </v-card>
      </v-col>
      <v-col>
        <v-card> <v-card-title>Schema</v-card-title></v-card>
      </v-col>
    </v-row>
    <v-row />
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "SourceDetailsTab",

  computed: {
    ...mapFields("source", ["selected.schema", "selected.example_log", "selected.loading"]),
  },

  data() {
    return {
      labels: ["12am", "3am", "6am", "9am", "12pm", "3pm", "6pm", "9pm"],
      value: [200, 675, 410, 390, 310, 460, 250, 240],
    }
  },
}
</script>
