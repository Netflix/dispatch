<template>
  <v-select
    v-model="incident_types"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Add incident types"
    multiple
    chips
    return-object
    :loading="loading"
  />
</template>

<script>
import IncidentTypeApi from "@/incident_type/api"
import _ from "lodash"
export default {
  name: "IncidentTypeMultiSelect",

  props: {
    value: {
      type: Array,
      default: function() {
        return []
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
    incident_types: {
      get() {
        return _.cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
    }
  },

  created() {
    this.error = null
    this.loading = true
    IncidentTypeApi.getAll({ itemsPerPage: 50, sortBy: ["name"], descending: [false] }).then(
      response => {
        this.items = response.data.items
        this.loading = false
      }
    )
  }
}
</script>
