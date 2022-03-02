<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" sm="6" md="8">
        <v-card height="100%">
          <v-toolbar flat>
            <v-toolbar-title>Documentation</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn icon color="info" :loading="loading" @click="save()">
              <v-icon>save</v-icon>
            </v-btn>
            <template v-slot:extension>
              <v-tabs v-model="tab">
                <v-tabs-slider></v-tabs-slider>
                <v-tab key="view">View </v-tab>
                <v-tab key="edit">Edit </v-tab>
              </v-tabs>
            </template>
          </v-toolbar>
          <v-tabs-items v-model="tab">
            <v-tab-item key="view">
              <v-card flat>
                <v-card-text>
                  <vue-markdown :source="documentation"></vue-markdown>
                </v-card-text>
              </v-card>
            </v-tab-item>
            <v-tab-item key="edit">
              <v-card flat>
                <v-card-text>
                  <div style="height: 400px">
                    <MonacoEditor
                      v-model="documentation"
                      :options="editorOptions"
                      language="markdown"
                    ></MonacoEditor>
                  </div>
                  <v-divider class="my-2"></v-divider>
                  <v-icon class="mr-2" small> mdi-language-markdown </v-icon>
                  <span class="text-caption grey--text">Styling with markdown supported</span>
                </v-card-text>
              </v-card>
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
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
              <v-list-item-title>Data Last Loaded At</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ data_last_loaded_at | formatRelativeDate }}</v-list-item-subtitle
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
            <v-data-table hide-default-footer disable-pagination :headers="headers" :items="links">
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
import VueMarkdown from "vue-markdown"

export default {
  name: "SourceDetailsTab",

  components: {
    VueMarkdown,
    MonacoEditor: () => import("monaco-editor-vue"),
  },

  computed: {
    ...mapFields("source", [
      "selected.name",
      "selected.description",
      "selected.owner",
      "selected.documentation",
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
      "selected.data_last_loaded_at",
      "selected.sampling_rate",
      "selected.loading",
    ]),
  },

  data() {
    return {
      tab: "view",
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
      },
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

  methods: {
    save() {
      const self = this
      this.$store.dispatch("source/save").then(function (data) {
        self.$emit("new-source-created", data)
      })
    },
  },
}
</script>
