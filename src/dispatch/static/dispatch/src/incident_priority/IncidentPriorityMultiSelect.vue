<template>
  <v-select
    v-model="incident_priorities"
    :items="items"
    item-text="name"
    :menu-props="{ maxHeight: '400' }"
    label="Add Incident Priorities"
    multiple
    chips
    return-object
    :loading="loading"
  />
</template>

<script>
import IncidentPriorityApi from "@/incident_priority/api"
import { cloneDeep } from "lodash"
export default {
  name: "IncidentPriorityMultiSelect",
  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    project: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
    }
  },

  computed: {
    incident_priorities: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  created() {
    this.error = null
    this.loading = "error"
    IncidentPriorityApi.getAll().then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
