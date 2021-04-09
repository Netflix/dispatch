<template>
  <v-card class="widget-card" outlined elevation="0">
    <v-card-text class="pa-0">
      <v-container class="pa-0">
        <div class="layout row ma-0">
          <div class="sm4 xs4 flex">
            <div class="layout column ma-0 justify-center align-center">
              <v-icon size="76px">
                {{ icon }}
              </v-icon>
            </div>
          </div>
          <div class="layout column ma-0 justify-center">
            <span class="caption">{{ subTitle }}</span>
            <div class="headline">
              {{ title }}
            </div>
            <span class="caption">{{ supTitle }}</span>
          </div>
        </div>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    supTitle: {
      type: String,
      default: "",
    },
    subTitle: {
      type: String,
      default: "",
    },
    title: {
      type: [Number, String],
      default: "",
    },
    icon: {
      type: String,
      default: "",
    },
    color: {
      type: String,
      default: "",
    },
  },

  data() {
    return {}
  },
}
</script>
