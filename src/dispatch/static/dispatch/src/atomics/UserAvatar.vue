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
})

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
    const avatarTemplate = import.meta.env.VITE_DISPATCH_AVATAR_TEMPLATE
    const stem = avatarTemplate.replace("*", userId)
    const loc = `${window.location.protocol}//${window.location.host}${stem}`
    return loc
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

const hasValidImage = computed(() => Boolean(effectiveImageUrl.value))

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
