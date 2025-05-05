<script setup>
import { defineProps, computed } from "vue"
import DTooltip from "@/components/DTooltip.vue"

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    default: "",
  },
  imageUrl: {
    type: String,
    default: "",
  },
  size: {
    type: [Number, String],
    default: 24,
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
  // New prop to force gradient in specific component instances
  forceGradient: {
    type: Boolean,
    default: false,
  },
})

// Check if we should force gradient display from environment variable
const forceGradientFromEnv = import.meta.env.VITE_DISPATCH_FORCE_AVATAR_GRADIENT === "true"

// Generate a color gradient based on the user's name
const getAvatarGradient = (name) => {
  let hash = 5381
  for (let i = 0; i < name.length; i++) {
    hash = ((hash << 5) + hash) ^ name.charCodeAt(i) // Using XOR operator for better distribution
  }

  const hue = Math.abs(hash) % 360 // Ensure hue is a positive number
  const fromColor = `hsl(${hue}, 95%, 50%)`
  const toColor = `hsl(${(hue + 120) % 360}, 95%, 50%)` // Getting triadic color by adding 120 to hue

  return `linear-gradient(${fromColor}, ${toColor})`
}

// Get avatar URL from email if provided
const getAvatarUrlFromEmail = (email) => {
  if (!email) return ""

  const userId = email.split("@")[0]
  if (userId) {
    const avatarTemplate = import.meta.env.VITE_DISPATCH_AVATAR_TEMPLATE || "/avatar/*/128x128.jpg"
    // Use a regular expression with the global flag to replace all occurrences of "*"
    const stem = avatarTemplate.replace(/\*/g, userId)

    // Use the base URL from environment variable if available, otherwise use window.location
    const envBaseUrl = import.meta.env.VITE_DISPATCH_AVATAR_BASE_URL
    const defaultBaseUrl = `${window.location.protocol}//${window.location.host}`
    const baseUrl = envBaseUrl || defaultBaseUrl
    return `${baseUrl}${stem}`
  }

  return ""
}

// Determine if we should show the image or the gradient
const effectiveImageUrl = computed(() => {
  // Use provided imageUrl if available
  if (props.imageUrl) return props.imageUrl

  // Otherwise try to generate one from email
  return getAvatarUrlFromEmail(props.email)
})

// Check if we should show the image or the gradient
const hasValidImage = computed(() => {
  // If force gradient is enabled (either via prop or env var), always show gradient
  if (props.forceGradient || forceGradientFromEnv) {
    return false
  }

  // Otherwise, check if we have a URL
  return Boolean(effectiveImageUrl.value)
})

// Get the tooltip text (use provided text or fall back to name)
const displayTooltipText = computed(() => props.tooltipText || props.name)

// Compute avatar style including border if enabled
const avatarStyle = computed(() => {
  if (props.border) {
    return {
      border: `2px solid ${props.borderColor}`,
    }
  }
  return {}
})

// Compute background style for gradient avatar
const gradientStyle = computed(() => {
  return {
    background: getAvatarGradient(props.name),
  }
})
</script>

<template>
  <div class="user-avatar-wrapper">
    <DTooltip v-if="showTooltip" :text="displayTooltipText">
      <template #activator="{ tooltip }">
        <v-avatar v-bind="tooltip" :size="size" class="user-avatar" :style="avatarStyle">
          <v-img v-if="hasValidImage" :src="effectiveImageUrl" />
          <div v-else class="gradient-avatar" :style="gradientStyle" />
        </v-avatar>
      </template>
    </DTooltip>
    <v-avatar v-else :size="size" class="user-avatar" :style="avatarStyle">
      <v-img v-if="hasValidImage" :src="effectiveImageUrl" />
      <div v-else class="gradient-avatar" :style="gradientStyle" />
    </v-avatar>
  </div>
</template>

<style scoped>
.user-avatar-wrapper {
  display: inline-flex;
}

.gradient-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
