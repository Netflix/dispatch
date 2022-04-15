<template>
  <v-text-field v-model="color" :label="label">
    <template v-slot:append-outer>
      <v-menu v-model="menu" top nudge-bottom="105" nudge-left="16" :close-on-content-click="false">
        <template v-slot:activator="{ on }">
          <div :style="swatchStyle" v-on="on" />
        </template>
        <v-card>
          <v-card-text class="pa-0">
            <v-color-picker
              v-model="color"
              show-swatches
              hide-sliders
              hide-inputs
              hide-mode-switch
              flat
            />
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
    value: {
      type: String,
      default: "#1976D2FF",
    },
    label: {
      type: String,
      default: function () {
        return "Color"
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
        return this.value || "#1976D2FF"
      },
      set(value) {
        this.$emit("input", value)
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
