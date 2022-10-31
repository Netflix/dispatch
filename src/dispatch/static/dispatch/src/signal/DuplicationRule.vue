<template>
  <v-card flat tile>
    <v-app-bar color="white" flat>
      <v-toolbar-title class="subtitle-2"> Duplication Configuration </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-tooltip max-width="250px" bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon v-bind="attrs" v-on="on"> help_outline </v-icon>
        </template>
        Dispatch will attempt to deduplicate signals that match the given criteria.
      </v-tooltip>
    </v-app-bar>
    <v-card-text>
      <v-row no-gutters>
        <v-col cols="12">
          <tag-type-combobox label="Anchors" v-model="tag_types"></tag-type-combobox>
        </v-col>
        <v-col cols="12">
          <v-select
            v-model="window"
            :items="windows"
            item-text="label"
            item-value="value"
            hint="This is a sliding window, all signals that were created in the given window will be
                considered for duplication."
            persistent-hint
            label="Window"
          ></v-select>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { cloneDeep } from "lodash"
import TagTypeCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "SignalDuplicationRuleCard",

  props: {
    value: {
      type: Object,
      default: function () {
        return {
          id: null,
          window: 600,
          tag_types: [],
        }
      },
    },
  },

  components: {
    TagTypeCombobox,
  },

  data() {
    return {
      windows: [
        { label: "10 min", value: 600 },
        { label: "30 min", value: 1800 },
        { label: "1 hr", value: 3600 },
        { label: "8 hr", value: 28800 },
        { label: "24 hr", value: 86400 },
      ],
    }
  },

  computed: {
    window: {
      get() {
        return this.value ? cloneDeep(this.value.window) : 600
      },
      set(value) {
        this.$emit("input", { id: this.id, window: value, tag_types: this.tag_types })
      },
    },
    tag_types: {
      get() {
        return this.value ? cloneDeep(this.value.tag_types) : []
      },
      set(value) {
        this.$emit("input", { id: this.id, window: this.window, tag_types: value })
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
