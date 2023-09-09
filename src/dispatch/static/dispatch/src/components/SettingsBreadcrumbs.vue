<template>
  <v-breadcrumbs :items="crumbs">
    <template #divider>
      <v-icon>mdi-chevron-right</v-icon>
    </template>
    <template #item="{ item }">
      <v-breadcrumbs-item v-if="item.projectSelect">
        <project-menu-select v-model="project" />
      </v-breadcrumbs-item>
      <v-breadcrumbs-item v-else :to="item.to" :disabled="item.disabled" class="text-capitalize">
        {{ item.text }}
      </v-breadcrumbs-item>
    </template>
  </v-breadcrumbs>
</template>

<script>
import ProjectMenuSelect from "@/project/ProjectMenuSelect.vue"

export default {
  name: "SettingsBreadCrumbs",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    organization: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  components: {
    ProjectMenuSelect,
  },

  computed: {
    project: {
      get() {
        return this.value[0]
      },
      set(value) {
        this.$emit("input", [value])
      },
    },
    crumbs() {
      return [
        {
          text: "Settings",
          disabled: false,
        },
        {
          projectSelect: true,
        },
        {
          text: this.$route.meta.title,
          disabled: false,
        },
      ]
    },
  },
}
</script>
