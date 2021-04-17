<template>
  <v-navigation-drawer v-model="showCreateEdit" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
          <v-list-item-title v-else class="title"> New </v-list-item-title>
          <v-list-item-subtitle>Plugin</v-list-item-subtitle>
        </v-list-item-content>
        <v-btn icon color="info" :loading="loading" @click="save()">
          <v-icon>save</v-icon>
        </v-btn>
        <v-btn icon color="secondary" @click="closeCreateEdit">
          <v-icon>close</v-icon>
        </v-btn>
      </v-list-item>
    </template>
    <v-card flat>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <span class="subtitle-2">Details</span>
            </v-flex>
            <v-flex xs12>
              <plugin-combobox label="Plugin" v-model="plugin" />
            </v-flex>
            <v-flex xs12>
              <span class="subtitle-2">Plugin Configuration</span>
              <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                  <v-btn small icon @click="addConfigurationItem()" v-on="on">
                    <v-icon>add</v-icon>
                  </v-btn>
                </template>
                <span>Add Configuration Item</span>
              </v-tooltip>
              <v-row align="center" dense v-for="(meta, idx) in configuration" :key="meta.key">
                <v-col cols="12" sm="1">
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on }">
                      <v-btn small icon @click="removeConfigurationItem(idx)" v-on="on"
                        ><v-icon>remove</v-icon></v-btn
                      >
                    </template>
                    <span>Remove Configuration Item</span>
                  </v-tooltip>
                </v-col>
                <v-col cols="12" sm="5">
                  <v-text-field label="Key" v-model="meta.key" type="text" />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-text-field label="Value" v-model="meta.value" type="text" />
                </v-col>
              </v-row>
            </v-flex>
            <v-flex xs12>
              <v-checkbox
                v-model="enabled"
                hint="Each plugin type can only ever have one enabled plugin. Existing enabled plugins will be de-activated."
                label="Enabled"
              />
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { mapFields, mapMultiRowFields } from "vuex-map-fields"
import { mapActions, mapMutations } from "vuex"

import PluginCombobox from "@/plugin/PluginCombobox.vue"

export default {
  name: "PluginEditSheet",

  components: {
    PluginCombobox,
  },

  computed: {
    ...mapFields("plugin", [
      "selected.id",
      "selected.project",
      "selected.enabled",
      "selected.loading",
      "selected.plugin",
      "dialogs.showCreateEdit",
    ]),
    ...mapFields("route", ["query"]),
    ...mapMultiRowFields("plugin", ["selected.configuration"]),
  },

  methods: {
    ...mapActions("plugin", ["save", "closeCreateEdit"]),
    ...mapMutations("plugin", ["addConfigurationItem", "removeConfigurationItem"]),
  },

  created() {
    if (this.query.project) {
      this.project = { name: this.query.project }
    }
  },
}
</script>
