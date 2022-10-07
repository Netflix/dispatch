<template>
  <v-menu
    ref="menu"
    v-model="display"
    :close-on-content-click="false"
    :nudge-right="45"
    transition="scale-transition"
    max-width="290px"
    min-width="290px"
  >
    <template v-slot:activator="{ on }">
      <v-list-item-avatar v-on="on" v-if="value" :color="value.color ? value.color : 'grey'">
        <span class="white--text">{{ value.name | initials }}</span>
      </v-list-item-avatar>
      <v-list-item-avatar v-on="on" v-else color="grey">
        <span class="white--text"></span>
      </v-list-item-avatar>
    </template>
    <v-card>
      <v-card-text class="px-0 py-0">
        <project-menu-select v-model="value" />
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <slot name="actions" :parent="this">
          <v-btn text @click="okHandler">Ok</v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>
<script>
import ProjectMenuSelect from "@/project/ProjectMenuSelect.vue"

export default {
  name: "ProjectPickerMenu",

  props: {
    value: {
      type: Object,
      default: function () {
        return { name: "N/A", color: "grey" }
      },
    },
  },

  components: {
    ProjectMenuSelect,
  },

  data() {
    return {
      display: false,
    }
  },

  computed: {},
  methods: {
    showProjectPicker() {
      this.display = true
    },
    okHandler() {
      this.display = false
    },
  },
}
</script>
