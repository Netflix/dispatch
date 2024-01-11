<template>
  <v-autocomplete
    v-model="project"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    variant="outlined"
    return-object
    hide-details
    :loading="loading"
    density="compact"
  >
    <template #item="{ item: { raw: item }, props }">
      <v-list-item v-bind="props">
        <v-list-item-subtitle :title="item.description">
          {{ item.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import ProjectApi from "@/project/api"

export default {
  name: "ProjectMenuSelect",

  props: {
    modelValue: {
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
        return this.modelValue
      },
      set(value) {
        this.$emit("update:modelValue", value)
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
