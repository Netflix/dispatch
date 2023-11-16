<template>
  <v-card variant="outlined">
    <v-card-text class="pa-0">
      <v-container>
        <v-row dense>
          <v-col cols="4" class="d-flex align-center justify-center">
            <v-icon size="76">
              {{ icon }}
            </v-icon>
          </v-col>
          <v-col class="d-flex flex-column justify-center">
            <span class="text-caption">{{ subTitle }}</span>
            <div class="text-h5">
              {{ title }}
            </div>
            <span class="text-caption">{{ supTitle }}</span>
          </v-col>
        </v-row>
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
