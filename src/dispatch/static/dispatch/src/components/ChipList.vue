<template>
  <span>
    <div class="text-caption">
      {{ label }}
      <v-chip
        v-for="(item, idx) in items"
        :key="item.id"
        close
        class="ma-1"
        @click:close="remove(idx)"
        :color="item.color ? item.color : 'grey'"
        label
        >{{ item.name }}</v-chip
      >
      <v-btn icon><v-icon>mdi-plus</v-icon></v-btn>
    </div>
  </span>
</template>

<script>
export default {
  name: "ChipList",

  components: {},
  data() {
    return {}
  },

  props: {
    items: {
      default: function () {
        return []
      },
      type: Array,
    },
    label: {
      type: String,
      default: function () {
        return "Incidents"
      },
    },
    loading: {
      default: function () {
        return false
      },
      type: [String, Boolean],
    },
  },

  methods: {
    remove(idx) {
      this.items.splice(idx)
    },
  },
}
</script>
