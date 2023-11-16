<template>
  <v-breadcrumbs :items="crumbs">
    <template #divider>
      <v-icon>mdi-chevron-right</v-icon>
    </template>
    <template #title="{ item }">
      <template v-if="item.projectSelect">
        <project-menu-select v-model="project" />
      </template>
      <template v-else>
        {{ item.title }}
      </template>
    </template>
    <template #item="{ item }">
      <v-breadcrumbs-item v-if="item.projectSelect">
        <project-menu-select v-model="project" />
      </v-breadcrumbs-item>
      <v-breadcrumbs-item v-else :to="item.to" :disabled="item.disabled" class="text-capitalize">
        {{ item.title }}
      </v-breadcrumbs-item>
    </template>
  </v-breadcrumbs>
</template>

<script>
import ProjectMenuSelect from "@/project/ProjectMenuSelect.vue"

export default {
  name: "SettingsBreadCrumbs",

  props: {
    modelValue: {
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
        return this.modelValue[0]
      },
      set(value) {
        this.$emit("update:modelValue", [value])
      },
    },
    crumbs() {
      return [
        {
          title: "Settings",
          disabled: false,
        },
        {
          projectSelect: true,
        },
        {
          title: this.$route.meta.title,
          disabled: false,
        },
      ]
    },
  },
}
</script>
