<script setup>
import { ref, watchEffect } from "vue"

const props = defineProps({
  buttons: {
    type: Array,
    default: () => [],
  },
  buttonHeight: {
    type: String,
    default: "24px",
  },
  initialTab: {
    type: String,
    default: "",
  },
})

const selectedTab = ref(props.initialTab)

watchEffect(() => {
  emit("update:selectedTab", selectedTab.value)
})
</script>

<template>
  <div>
    <div class="button-group-container">
      <v-btn-toggle
        v-model="selectedTab"
        mandatory
        variant="outlined"
        rounded="lg"
        selected-class="selected-button"
      >
        <v-btn
          v-for="button in buttons"
          :key="button.value"
          class="text-subtitle-2 unselected-button"
          :height="buttonHeight"
          :value="button.value"
          variant="plain"
          :disabled="button.disabled"
        >
          <slot :name="button.value" v-bind="button">
            <span class="button-text">{{ button.text }}</span>
            <v-badge v-if="button.badge" inline :content="button.badge" class="small-badge" />
          </slot>
        </v-btn>
      </v-btn-toggle>
    </div>
  </div>
</template>

<style scoped>
.v-tab {
  text-transform: initial;
  color: #272727;
  font-weight: 400;
  letter-spacing: normal;
  line-height: 1.5;
  font-family: "Inter", sans-serif;
}

.tab {
  transition: all 0.2s ease;
}

.button-group-container {
  background-color: rgb(244, 245, 248);
  padding-right: 0px;
  padding-left: 0px;
  margin-bottom: 10px;
  border-radius: 8px;
  z-index: 1;
  height: 24px !important;

  transform: scale(0.95);
  display: inline-flex;
}

.selected-button {
  background: white !important;
  background-color: white !important;
  color: white !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px;
  border: 1px solid black !important;
  border-color: rgb(223, 225, 228) !important;
  height: 24px !important;
  border-width: 1px;
  border-radius: 7px !important;
}

.small-badge {
  transform: scale(0.9);
}

.selected-button .button-text {
  color: rgb(40, 42, 28) !important;
}

.selected-button.v-btn--variant-plain {
  opacity: 1 !important;
}
</style>
