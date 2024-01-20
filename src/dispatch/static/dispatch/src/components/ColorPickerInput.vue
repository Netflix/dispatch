<template>
  <v-text-field v-model="color" :label="label">
    <template #append>
      <v-menu v-model="menu" location="top" :close-on-content-click="false">
        <template #activator="{ props }">
          <div :style="swatchStyle" v-bind="props" />
        </template>
        <v-card>
          <v-card-text class="pa-0">
            <v-color-picker v-model="color" show-swatches hide-sliders hide-inputs />
          </v-card-text>
        </v-card>
      </v-menu>
    </template>
  </v-text-field>
</template>

<script>
export default {
  name: "ColorPickerInput",

  props: {
    modelValue: {
      type: String,
      default: "#1976D2FF",
    },
    label: {
      type: String,
      default: function () {
        return "Color"
      },
    },
    default: {
      type: String,
      default: function () {
        return "#1976D2FF"
      },
    },
  },

  data() {
    return {
      menu: false,
    }
  },

  computed: {
    color: {
      get() {
        return this.modelValue || this.default || "#1976D2FF"
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
    swatchStyle() {
      const { color, menu } = this
      return {
        backgroundColor: color,
        cursor: "pointer",
        height: "30px",
        width: "30px",
        borderRadius: menu ? "50%" : "4px",
        transition: "border-radius 200ms ease-in-out",
      }
    },
  },
}
</script>
