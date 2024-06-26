<template>
  <v-container>
    <v-row no-gutter>
      <span class="text-subtitle-2">Plugin Metadata</span>
      <v-spacer />
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <v-btn size="small" icon variant="text" @click="addPlugin()" v-bind="props">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </template>
        <span>Add Plugin</span>
      </v-tooltip>
    </v-row>
    <span v-for="(plugin, plugin_idx) in plugins" :key="plugin_idx">
      <v-row align="center" dense>
        <v-col cols="12" sm="1">
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn
                size="small"
                icon
                variant="text"
                @click="removePlugin(plugin_idx)"
                v-bind="props"
                ><v-icon>mdi-minus</v-icon></v-btn
              >
            </template>
            <span>Remove Plugin</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="10">
          <plugin-instance-combobox
            :model-value="plugin"
            @update:model-value="setPlugin({ plugin: $event, idx: plugin_idx })"
            :project="project"
            :type="type"
            label="Plugin"
          />
        </v-col>
        <v-col cols="12" sm="1">
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn size="small" icon variant="text" @click="addItem(plugin_idx)" v-bind="props"
                ><v-icon>mdi-plus</v-icon></v-btn
              >
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
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <v-btn
                size="small"
                icon
                variant="text"
                @click="removeItem(plugin_idx, meta_idx)"
                v-bind="props"
                ><v-icon>mdi-minus</v-icon></v-btn
              >
            </template>
            <span>Remove Item</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field
            label="Key"
            @update:model-value="itemChanged()"
            v-model="meta.key"
            type="text"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field
            label="Value"
            @update:model-value="itemChanged()"
            v-model="meta.value"
            type="text"
          />
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
    modelValue: {
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
        return cloneDeep(this.modelValue).map((x) => ({ ...x, ...{ plugin: { slug: x.slug } } }))
      },
    },
  },

  methods: {
    addPlugin() {
      this.plugins.push({ plugin: { slug: "" } })
      this.$emit("update:modelValue", this.plugins)
    },
    removePlugin(plugin_idx) {
      this.plugins.splice(plugin_idx, 1)
      this.$emit("update:modelValue", this.plugins)
    },
    addItem(plugin_idx) {
      if (!this.plugins[plugin_idx].metadata) {
        this.plugins[plugin_idx].metadata = []
      }
      this.plugins[plugin_idx].metadata.push({ key: "", value: "" })
      this.$emit("update:modelValue", this.plugins)
    },
    removeItem(plugin_idx, metadata_idx) {
      this.plugins[plugin_idx].metadata.splice(metadata_idx, 1)
      this.$emit("update:modelValue", this.plugins)
    },
    setPlugin(event) {
      this.plugins[event.idx] = event.plugin
      this.plugins[event.idx].slug = event.plugin.plugin.slug
      this.$emit("update:modelValue", this.plugins)
    },
    itemChanged() {
      this.$emit("update:modelValue", this.plugins)
    },
  },
}
</script>
