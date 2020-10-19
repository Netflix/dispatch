<template>
  <v-container>
    <v-row no-gutter>
      <span class="subtitle-2">Plugin Metadata</span>
      <v-spacer />
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn small icon @click="addPlugin()" v-on="on"><v-icon>add</v-icon></v-btn>
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
          <plugin-combobox
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
      <v-row align="center" dense v-for="meta in plugin.metadata" :key="meta.key">
        <v-col cols="12" sm="1">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small icon @click="removeItem(plugin)" v-on="on"
                ><v-icon>remove</v-icon></v-btn
              >
            </template>
            <span>Remove Item</span>
          </v-tooltip>
        </v-col>
        <v-col cols="12" sm="5">
          <v-text-field label="Key" v-model="meta.key" type="text"></v-text-field>
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field label="Value" v-model="meta.value" type="text"></v-text-field>
        </v-col>
      </v-row>
    </span>
  </v-container>
</template>

<script>
import PluginCombobox from "@/plugin/PluginCombobox.vue"
export default {
  name: "PluginMetadataInput",

  components: {
    PluginCombobox
  },

  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    }
  },

  computed: {
    plugins: {
      get() {
        return [...this.value]
      }
    }
  },

  methods: {
    addPlugin() {
      this.plugins.push({ title: null, slug: null, metadata: [{ key: "", value: "" }] })
      this.$emit("input", this.plugins)
    },
    removePlugin(idx) {
      this.plugins.splice(idx)
      this.$emit("input", this.plugins)
    },
    addItem(plugin) {
      plugin.metadata.push({ key: null, value: null })
      this.$emit("input", this.plugins)
    },
    removeItem(plugin, idx) {
      plugin.metadata.splice(idx)
      this.$emit("input", this.plugins)
    },
    setPlugin(event) {
      if (!event.plugin.metadata) {
        event.plugin.metadata = [{ key: null, value: null }]
      }
      this.plugins[event.idx] = event.plugin
      this.$emit("input", this.plugins)
    }
  }
}
</script>
