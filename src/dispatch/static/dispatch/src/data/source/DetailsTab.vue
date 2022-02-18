<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-card>
          <v-sheet color="blue">
            <v-sparkline
              :labels="labels"
              :value="value"
              color="white"
              line-width="1"
              height="50"
              padding="15"
            ></v-sparkline>
          </v-sheet>
          <v-card-text class="pt-0">
            <div class="text-h6 font-weight-light mb-2">Record Volume</div>
            <v-divider class="my-2"></v-divider>
            <v-icon class="mr-2" small> mdi-clock </v-icon>
            <span class="text-caption grey--text font-weight-light">last record 10min ago</span>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card> <v-card-title>Documentation</v-card-title></v-card>
      </v-col>
      <v-col>
        <v-card>
          <v-list-item two-line>
            <v-list-item-content>
              <v-list-item-title class="text-h5"> Basic Information </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            {{ description }}
          </v-list-item>
          <v-list class="transparent">
            <v-list-item>
              <v-list-item-title>Last Refreshed</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ last_refreshed | formatRelativeDate }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Retention</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ retention }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Avg Prop Delay</v-list-item-title>
              <v-list-item-subtitle class="text-right"> {{ delay }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Avg Daily Volume</v-list-item-title>
              <v-list-item-subtitle class="text-right"> {{ size }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Source Type</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source_type.name }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Data Format</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source_data_format.name }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Transport</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ source_transport.name }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Sampling Rate</v-list-item-title>
              <v-list-item-subtitle class="text-right"> {{ sampling_rate }}%</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card>
          <v-card-title>Links</v-card-title>
          <v-card-text>
            <v-data-table :headers="headers" :items="links">
              <template v-slot:item.name="{ item }">
                <span
                  ><a :href="item.href">
                    <b>{{ item.name }}</b></a
                  ></span
                >
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "SourceDetailsTab",

  components: {},

  computed: {
    ...mapFields("source", [
      "selected.name",
      "selected.description",
      "selected.owner",
      "selected.retention",
      "selected.source_environment",
      "selected.source_status",
      "selected.source_type",
      "selected.source_transport",
      "selected.source_data_format",
      "selected.links",
      "selected.size",
      "selected.delay",
      "selected.aggregation",
      "selected.external_id",
      "selected.project",
      "selected.last_refreshed",
      "selected.sampling_rate",
      "selected.loading",
    ]),
  },

  data() {
    return {
      labels: ["12am", "3am", "6am", "9am", "12pm", "3pm", "6pm", "9pm"],
      value: [200, 675, 410, 390, 310, 460, 250, 240],
      headers: [
        {
          text: "Name",
          align: "start",
          sortable: false,
          value: "name",
        },
        { text: "Description", value: "description" },
      ],
    }
  },
}
</script>
