<template>
  <v-autocomplete
    v-model="project"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    label="Project"
    item-title="name"
    return-object
    hide-details
    :loading="loading"
    variant="outlined"
    dense
  >
    <template #item="data">
      <v-list-item-title>{{ data.item.name }}</v-list-item-title>
      <v-list-item-subtitle style="width: 200px" class="text-truncate">
        {{ data.item.description }}
      </v-list-item-subtitle>
    </template>
  </v-autocomplete>
</template>

<script>
import ProjectApi from "@/project/api"

export default {
  name: "ProjectMenuSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
    }
  },

  computed: {
    project: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  created() {
    this.error = null
    this.loading = "error"
    let filterOptions = {
      itemsPerPage: 50,
      sortBy: ["name"],
      descending: [false],
    }

    ProjectApi.getAll(filterOptions).then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
