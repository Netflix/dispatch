<template>
  <div class="hover-container">
    <div class="hover-card rounded-lg">
      <v-card>
        <v-card-title class="text-subtitle-2 font-weight-regular">
          {{ item.raw.id }}
        </v-card-title>
        <v-card-text v-if="item.signal.external_url">
          <v-btn
            class="text-subtitle-2 font-weight-regular"
            prepend-icon="mdi-file-document"
            variant="text"
          >
            Document
          </v-btn>
          <v-btn
            class="text-subtitle-2 font-weight-regular"
            prepend-icon="mdi-pencil"
            variant="text"
          >
            Edit
          </v-btn>
        </v-card-text>
      </v-card>
    </div>
    <slot></slot>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.hover-container {
  position: relative;
}

.v-card {
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 4px !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px !important;
  color: rgb(60, 65, 73) !important;
  opacity: 2 !important;
  background-color: rgba(255, 255, 255, 0.5) !important;
}

.hover-card {
  visibility: hidden;
  position: absolute;
  bottom: 100%;
  width: 300px;
  opacity: 0;
  transition: opacity 0.1s linear, visibility 0.5s linear;
  transform: translateY(4px);
}

.hover-container:hover .hover-card {
  visibility: visible;
  opacity: 1;
  transition-delay: 0s !important;
}
</style>
