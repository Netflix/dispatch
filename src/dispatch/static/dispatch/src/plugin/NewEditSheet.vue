<template>
  <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
    <template #prepend>
      <v-list-item lines="two">
        <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
        <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
        <v-list-item-subtitle>Plugin Instance</v-list-item-subtitle>
        <template #append>
          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!valid"
            @click="save()"
          >
            <v-icon>mdi-content-save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeCreateEdit">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-list-item>
    </template>
    <v-card>
      <v-card-text>
        <v-form v-model="valid">
          <plugin-combobox v-if="!id" label="Plugin" v-model="plugin" />
          <v-checkbox
            v-model="enabled"
            hint="Each plugin type can only ever have one enabled plugin. Existing enabled plugins will be de-activated."
            label="Enabled"
          />
          <!-- <json-form
            v-if="!plugin"
            v-model="configuration"
            :schema="configuration_schema"
            :options="options"
          />
          <json-form
            v-else
            v-model="configuration"
            :schema="plugin.configuration_schema"
            :options="options"
          /> -->
          <FormKit type="form" v-model="configuration" :actions="false">
            <FormKitSchema :schema="formkit_configuration_schema" />
          </FormKit>
        </v-form>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
// import jsonForm from "@koumoul/vjsf"
// import "@koumoul/vjsf/dist/main.css"
import { mapFields } from "vuex-map-fields"
import { mapActions, mapMutations } from "vuex"

import PluginCombobox from "@/plugin/PluginCombobox.vue"

export default {
  name: "PluginEditSheet",

  components: {
    // jsonForm,
    PluginCombobox,
  },

  data() {
    return {
      valid: false,
      options: {
        initialValidation: "all",
      },
    }
  },

  computed: {
    ...mapFields("plugin", [
      "selected.id",
      "selected.project",
      "selected.enabled",
      "selected.configuration",
      "selected.configuration_schema",
      "selected.formkit_configuration_schema",
      "selected.loading",
      "selected.plugin",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("plugin", ["save", "closeCreateEdit"]),
    ...mapMutations("plugin", ["addConfigurationItem", "removeConfigurationItem"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
