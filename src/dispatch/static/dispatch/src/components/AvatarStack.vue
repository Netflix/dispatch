<template>
  <v-container>
    <div class="d-flex align-center" style="position: relative">
      <v-avatar
        v-for="(item, index) in shownItems"
        :key="index"
        color="indigo"
        class="ma-1 overlapped-avatar"
        size="50"
        :style="`right: ${index * 25}px`"
      >
        {{ item }}
      </v-avatar>

      <v-menu offset-y v-model="menu" :close-on-content-click="false">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            icon
            v-if="overflowItems.length"
            v-bind="attrs"
            class="overlapped-avatar"
            :style="`right: ${shownItems.length * 25}px`"
            v-on="on"
          >
            <v-icon>mdi-dots-horizontal</v-icon>
          </v-btn>
        </template>

        <v-card>
          <v-card-title>Additional Items</v-card-title>
          <v-card-text>
            <v-chip v-for="(item, index) in overflowItems" :key="'overflown-' + index" class="ma-2">
              {{ item }}
            </v-chip>
          </v-card-text>
        </v-card>
      </v-menu>
    </div>
  </v-container>
</template>

<script>
import { ref, computed, watchEffect } from "vue"

export default {
  name: "AvatarStack",
  props: {
    modelValue: Array,
    default: () => [],
    required: true,
  },
  emits: ["update:modelValue"],

  setup(props, { emit }) {
    const items = ref(props.modelValue)
    const menu = ref(false)
    const maxVisibleItems = ref(3)

    const shownItems = computed(() => items.value.slice(0, maxVisibleItems.value))
    const overflowItems = computed(() => items.value.slice(maxVisibleItems.value))

    watchEffect(() => {
      items.value = props.modelValue
    })

    watchEffect(() => {
      emit("update:modelValue", items.value)
    })

    return { items, menu, maxVisibleItems, shownItems, overflowItems }
  },
}
</script>

<style scoped>
.overlapped-avatar {
  position: absolute;
}
</style>
