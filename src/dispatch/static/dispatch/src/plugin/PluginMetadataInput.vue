<template>
  <v-container>
    <v-row no-gutter>
      <span class="subtitle-2">Plugin Metadata</span>
      <v-spacer />
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn small icon @click="addPlugin()" v-on="on">
            <v-icon>add</v-icon>
          </v-btn>
        </template>
        <span>Add Plugin</span>
      </v-tooltip>
    </v-row>
    <span v-for="(plugin, plugin_idx) in plugins" :key="plugin_idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removePlugin(plugin_idx)" v-on="on"
                ><v-icon>remove</v-icon></v-btn
              >
            </template>
            <span>Remove Plugin</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="10">
          <plugin-instance-combobox
            :project="project"
            :type="type"
            @input="setPlugin({ plugin: $event, idx: plugin_idx })"
            label="Plugin"
            :value="plugin"
          />
        </v-col>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="addItem(plugin_idx)" v-on="on"><v-icon>add</v-icon></v-btn>
            </template>
            <span>Add Item</span>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row
        align="center"
        dense
        v-for="(meta, meta_idx) in plugin.metadata"
        :key="meta_idx"
        :plugin-index="plugin_idx"
      >
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeItem(plugin_idx, meta_idx)" v-on="on"
                ><v-icon>remove</v-icon></v-btn
              >
            </template>
            <span>Remove Item</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field label="Key" @input="itemChanged()" v-model="meta.key" type="text" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field label="Value" @input="itemChanged()" v-model="meta.value" type="text" />
        </v-col>
      </v-row>
    </span>
  </v-container>
</template>

<script>
import { cloneDeep } from "lodash"
import PluginInstanceCombobox from "@/plugin/PluginInstanceCombobox.vue"
export default {
  name: "PluginMetadataInput",

  components: {
    PluginInstanceCombobox,
  },

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    project: {
      type: Object,
      default: null,
    },
    type: {
      type: String,
      default: null,
    },
  },

  computed: {
    plugins: {
      get() {
        return cloneDeep(this.value).map((x) => ({ ...x, ...{ plugin: { slug: x.slug } } }))
      },
    },
  },

  methods: {
    addPlugin() {
      this.plugins.push({ plugin: { slug: "" } })
      this.$emit("input", this.plugins)
    },
    removePlugin(plugin_idx) {
      this.plugins.splice(plugin_idx, 1)
      this.$emit("input", this.plugins)
    },
    addItem(plugin_idx) {
      if (!this.plugins[plugin_idx].metadata) {
        this.$set(this.plugins[plugin_idx], "metadata", [])
      }
      this.plugins[plugin_idx].metadata.push({ key: "", value: "" })
      this.$emit("input", this.plugins)
    },
    removeItem(plugin_idx, metadata_idx) {
      this.plugins[plugin_idx].metadata.splice(metadata_idx, 1)
      this.$emit("input", this.plugins)
    },
    setPlugin(event) {
      this.$set(this.plugins, event.idx, event.plugin)
      this.plugins[event.idx].slug = event.plugin.plugin.slug
      this.$emit("input", this.plugins)
    },
    itemChanged() {
      this.$emit("input", this.plugins)
    },
  },
}
</script>
