<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" sm="6" md="8">
        <v-card height="100%">
          <v-toolbar>
            <v-toolbar-title>Documentation</v-toolbar-title>
            <v-spacer />
            <v-btn icon variant="text" color="info" :loading="loading" @click="save()">
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <template #extension>
              <v-tabs v-model="tab">
                <v-tab key="view">View </v-tab>
                <v-tab key="edit">Edit </v-tab>
              </v-tabs>
            </template>
          </v-toolbar>
          <v-window v-model="tab">
            <v-window-item key="view">
              <v-card>
                <v-card-text>
                  <vue-markdown :source="documentation" />
                </v-card-text>
              </v-card>
            </v-window-item>
            <v-window-item key="edit">
              <v-card>
                <v-card-text>
                  <div style="height: 400px">
                    <MonacoEditor
                      v-model="documentation"
                      :options="editorOptions"
                      language="markdown"
                    />
                  </div>
                  <v-divider class="my-2" />
                  <v-icon class="mr-2" size="small"> mdi-language-markdown </v-icon>
                  <span class="text-caption text-grey">Styling with markdown supported</span>
                </v-card-text>
              </v-card>
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>
      <v-col cols="6" md="4">
        <v-card>
          <v-list-item lines="two">
            <v-list-item-title class="text-h5"> Basic Information </v-list-item-title>
          </v-list-item>
          <v-list-item>
            {{ description }}
          </v-list-item>
          <v-list class="bg-transparent">
            <v-list-item>
              <v-list-item-title>Data Last Loaded At</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ formatRelativeDate(data_last_loaded_at) }}
              </v-list-item-subtitle>
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
                {{ source_type.name }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Data Format</v-list-item-title>
              <v-list-item-subtitle v-if="source_data_format" class="text-right">
                {{ source_data_format.name }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Transport</v-list-item-title>
              <v-list-item-subtitle v-if="source_transport" class="text-right">
                {{ source_transport.name }}
              </v-list-item-subtitle>
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
              <template #item.name="{ item }">
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
import VueMarkdown from "vue3-markdown-it"
import MonacoEditor from "@/components/MonacoEditor.vue"
import { formatRelativeDate } from "@/filters"

export default {
  name: "SourceDetailsTab",

  components: {
    VueMarkdown,
    MonacoEditor,
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
          title: "Name",
          align: "start",
          sortable: false,
          key: "name",
        },
        { title: "Description", key: "description" },
      ],
    }
  },

  setup() {
    return { formatRelativeDate }
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
