<script setup>
import { computed } from "vue"
import { useStore } from "vuex"
import UserAvatar from "@/atomics/UserAvatar.vue"

const store = useStore()
const props = defineProps({
  size: {
    type: [Number, String],
    default: 30,
  },
  showTooltip: {
    type: Boolean,
    default: false,
  },
  tooltipText: {
    type: String,
    default: "",
  },
  border: {
    type: Boolean,
    default: false,
  },
  borderColor: {
    type: String,
    default: "white",
  },
})

// Get current user from store
const currentUser = computed(() => {
  try {
    return store.state.auth.currentUser || {}
  } catch (e) {
    console.error("Error getting current user:", e)
    return {}
  }
})

// Get user name
const userName = computed(() => {
  return currentUser.value.name || currentUser.value.email || ""
})

// Get user email
const userEmail = computed(() => {
  return currentUser.value.email || ""
})

// Get avatar URL using the userAvatarUrl getter
const userAvatarUrl = computed(() => {
  try {
    if (store.getters["auth/userAvatarUrl"]) {
      return store.getters["auth/userAvatarUrl"](currentUser.value)
    }
  } catch (e) {
    console.error("Error getting avatar URL from store:", e)
  }
  return ""
})

// Get tooltip text
const displayTooltipText = computed(() => props.tooltipText || userName.value)
</script>

<template>
  <UserAvatar
    :name="userName"
    :email="userEmail"
    :imageUrl="userAvatarUrl"
    :size="size"
    :showTooltip="showTooltip"
    :tooltipText="displayTooltipText"
    :border="border"
    :borderColor="borderColor"
  />
</template>
