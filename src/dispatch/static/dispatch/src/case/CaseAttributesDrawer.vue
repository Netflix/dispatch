<template>
  <v-navigation-drawer location="right" width="300">
    <v-toolbar density="compact" color="transparent">
      <v-spacer></v-spacer>
      <!----<avatar-stack v-model="participants" />-->
      <v-btn icon>
        <v-icon>mdi-dots-vertical</v-icon>
      </v-btn>
      <case-toggle-visibility v-model="visibility" />
    </v-toolbar>
  </v-navigation-drawer>
</template>
<script>
import { computed } from "vue"
import AvatarStack from "@/components/AvatarStack.vue"
import CaseToggleVisibility from "@/case/CaseToggleVisibility.vue"

export default {
  name: "CaseAttributesDrawer",
  props: {
    modelValue: {
      type: Object,
      default: () => ({}),
      required: true,
    },
  },
  components: {
    AvatarStack,
    CaseToggleVisibility,
  },
  setup(props, { emit }) {
    const participants = computed({
      get: () => props.modelValue.participants,
      set: (value) => emit("update:modelValue", value),
    })

    const visibility = computed({
      get: () => props.modelValue.visibility,
      set: (value) => emit("update:modelValue", value),
    })

    return {
      participants,
      visibility,
    }
  },
}
</script>
