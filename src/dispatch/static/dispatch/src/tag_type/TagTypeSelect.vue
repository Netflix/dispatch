<template>
  <v-select
    v-model="tag_type"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Type"
    return-object
    :loading="loading"
  >
    <template v-slot:item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title v-text="data.item.name"></v-list-item-title>
          <v-list-item-subtitle v-text="data.item.description"></v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </template>
  </v-select>
</template>

<script>
import TagTypeApi from "@/tag_type/api"
import { cloneDeep } from "lodash"
export default {
  name: "TagTypeSelect",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    }
  },

  data() {
    return {
      loading: false,
      items: []
    }
  },

  computed: {
    tag_type: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
    }
  },

  created() {
    this.error = null
    this.loading = true
    TagTypeApi.getAll({ itemsPerPage: 50, sortBy: ["name"], descending: [false] }).then(
      response => {
        this.items = response.data.items
        this.loading = false
      }
    )
  }
}
</script>
