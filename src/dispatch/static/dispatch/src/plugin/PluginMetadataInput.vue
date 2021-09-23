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
    <span v-for="(plugin, idx) in plugins" :key="plugin.slug">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removePlugin(idx)" v-on="on"><v-icon>remove</v-icon></v-btn>
            </template>
            <span>Remove Plugin</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="10">
          <plugin-instance-combobox
            :project="project"
            :type="type"
            @input="setPlugin({ plugin: $event, idx: idx })"
            label="Plugin"
            :value="plugin"
          />
        </v-col>
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="addItem(plugin)" v-on="on"><v-icon>add</v-icon></v-btn>
            </template>
            <span>Add Item</span>
          </v-tooltip>
        </v-col>
      </v-row>
      <v-row align="center" dense v-for="(meta, index) in plugin.metadata" :key="index">
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeItem(plugin, index)" v-on="on"
                ><v-icon>remove</v-icon></v-btn
              >
            </template>
            <span>Remove Item</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field label="Key" v-model="meta.key" type="text" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field label="Value" v-model="meta.value" type="text" />
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

  data() {
    return {
      plugins: [],
    }
  },

  created() {
    this.plugins = cloneDeep(this.value)
  },

  methods: {
    addPlugin() {
      this.plugins.push({ title: null, slug: null, metadata: [{ key: "", value: "" }] })
    },
    removePlugin(idx) {
      this.plugins.splice(idx, 1)
    },
    addItem(plugin) {
      plugin.metadata.push({ key: "", value: "" })
    },
    removeItem(plugin, idx) {
      plugin.metadata.splice(idx, 1)
    },
    setPlugin(event) {
      if (!event.plugin.metadata) {
        event.plugin.metadata = [{ key: "", value: "" }]
      }
      this.plugins[event.idx] = event.plugin
    },
  },

  watch: {
    plugins: {
      deep: true,
      handler(val) {
        this.$emit("input", cloneDeep(val))
      },
    },
  },
}
</script>
