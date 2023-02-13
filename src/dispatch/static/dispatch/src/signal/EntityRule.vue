<template>
  <v-card flat tile>
    <v-app-bar color="white" flat>
      <v-toolbar-title class="subtitle-2"> Entity Type Configuration </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-tooltip max-width="250px" bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
        </template>
        Dispatch will attempt to locate entities that match the given criteria. Global entities cannot be selected, since they are applied to all signals.
      </v-tooltip>
    </v-app-bar>
    <v-card-text>
      <v-row no-gutters>
        <v-col cols="12">
          <entity-type-combobox label="Entity Types" v-model="entity_types"></entity-type-combobox>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { cloneDeep } from "lodash"
import EntityTypeCombobox from "@/entity_type/EntityTypeFilterCombobox.vue"

export default {
  name: "SignalEntityTypeRuleCard",

  props: {
    value: {
      type: [Object, Array],
      default: function () {
        return {
          entity_types: [],
        }
      },
    },
  },

  components: {
    EntityTypeCombobox,
  },

  computed: {
    entity_types: {
      get() {
        return this.value && (Array.isArray(this.value) ? cloneDeep(this.value) : cloneDeep(this.value.entity_types || []));
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    id: {
      get() {
        return this.value ? cloneDeep(this.value.id) : null
      },
    },
  },
}
</script>
