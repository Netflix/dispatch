<template>
  <div class="hover-container" @mousemove="updatePosition">
    <div class="hover-card rounded-lg">
      <v-card>
        <v-card-title>
          <div class="d-flex align-items-center">
            <v-avatar v-if="userAvatarUrl" class="mt-2">
              <v-img :src="userAvatarUrl" />
            </v-avatar>
            <div class="pl-3">
              <a class="link-no-underline" :href="item.weblink" target="_blank">
                <div class="text-overflow" style="max-width: 200px">
                  <span class="dispatch-text-subtitle">{{ item.name }}</span>
                  <span class="pl-1 text-medium-emphasis dispatch-text-paragraph text-caption">
                    ({{ item.email }})
                  </span>
                </div>
              </a>
              <div class="mt-n2">
                <span class="text-medium-emphasis dispatch-text-paragraph text-caption">
                  {{ item.title }}
                </span>
              </div>
            </div>
          </div>
        </v-card-title>
      </v-card>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"

import { IndividualContact } from "@/individual/individualContact"

const props = defineProps({
  item: Object as () => IndividualContact,
})

const avatarTemplate = import.meta.env.VITE_DISPATCH_AVATAR_TEMPLATE

const userAvatarUrl = computed(() => {
  if (!avatarTemplate) return ""
  const email = props.item.email || ""
  const userId = email.split("@")[0]
  if (userId) {
    const stem = avatarTemplate.replace("*", userId)
    const loc = `${window.location.protocol}//${window.location.host}${stem}`
    return loc
  }
  return ""
})
</script>

<style lang="scss" scoped>
@import "@/styles/index.scss";

.hover-container {
  position: relative;
  z-index: 99999 !important;
}

.v-card {
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 4px !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px !important;
  color: rgb(60, 65, 73) !important;
  opacity: 2 !important;
  background-color: rgba(255, 255, 255, 0.5) !important;
  max-width: 300px;
  z-index: 99999 !important;
}

.hover-card {
  visibility: hidden;
  position: absolute;
  bottom: 100%;
  opacity: 0;
  transition: opacity 0s, visibility 0s;
  max-width: 300px;
  z-index: 99999 !important;
}

.hover-container:hover .hover-card {
  visibility: visible;
  opacity: 1;
  transition: opacity 0s 0.9s, visibility 0s 0.9s;
}

.link-no-underline {
  text-decoration: none;
}

.text-overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
