<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-card>
          <v-list-item two-line>
            <v-list-item-content>
              <v-list-item-title class="text-h5"> Basic Information </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            {{ source.description }}
          </v-list-item>
          <v-list class="transparent">
            <v-list-item>
              <v-list-item-title>Last Refreshed</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source.lastRefreshed | formatRelativeDate }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Retention</v-list-item-title>
              <v-list-item-subtitle class="text-right"> 1 yr</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Avg Prop Delay</v-list-item-title>
              <v-list-item-subtitle class="text-right"> 1 hr</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Avg Daily Volume</v-list-item-title>
              <v-list-item-subtitle class="text-right"> 10m</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Source Type</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source.sourceType }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Data Format</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source.dataFormat }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Transport</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source.transport }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Sampling Rate</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source.samplingRate }}%</v-list-item-subtitle
              >
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      <v-col>
        <v-card> <v-card-title>Documentation</v-card-title></v-card>
      </v-col>
    </v-row>
    <v-row> </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "SourceDetailsTab",

  components: {},

  computed: {
    ...mapFields("source", ["selected.source", "selected.loading"]),
  },

  data() {
    return {
      labels: ["12am", "3am", "6am", "9am", "12pm", "3pm", "6pm", "9pm"],
      value: [200, 675, 410, 390, 310, 460, 250, 240],
      headers: [
        {
          text: "Dessert (100g serving)",
          align: "start",
          sortable: false,
          value: "name",
        },
        { text: "Calories", value: "calories" },
        { text: "Fat (g)", value: "fat" },
        { text: "Carbs (g)", value: "carbs" },
        { text: "Protein (g)", value: "protein" },
        { text: "Iron (%)", value: "iron" },
      ],
      desserts: [
        {
          name: "Frozen Yogurt",
          calories: 159,
          fat: 6.0,
          carbs: 24,
          protein: 4.0,
          iron: "1%",
        },
        {
          name: "Ice cream sandwich",
          calories: 237,
          fat: 9.0,
          carbs: 37,
          protein: 4.3,
          iron: "1%",
        },
        {
          name: "Eclair",
          calories: 262,
          fat: 16.0,
          carbs: 23,
          protein: 6.0,
          iron: "7%",
        },
        {
          name: "Cupcake",
          calories: 305,
          fat: 3.7,
          carbs: 67,
          protein: 4.3,
          iron: "8%",
        },
        {
          name: "Gingerbread",
          calories: 356,
          fat: 16.0,
          carbs: 49,
          protein: 3.9,
          iron: "16%",
        },
      ],
    }
  },
}
</script>
