<template>
  <v-container fluid>
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
              <v-list-item-subtitle v-if="source_type" class="text-right">
                {{ source_type.name }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Data Format</v-list-item-title>
              <v-list-item-subtitle v-if="source_data_format" class="text-right">
                {{ source_data_format.name }}</v-list-item-subtitle
              >
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Transport</v-list-item-title>
              <v-list-item-subtitle v-if="source_transport" class="text-right">
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
