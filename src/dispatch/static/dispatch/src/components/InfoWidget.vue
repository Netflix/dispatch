<style>
.info-card::before {
  background-color: #4969e4;
  display: block;
  content: "";
  position: absolute;
  top: 6px;
  bottom: 6px;
  left: -8px;
  width: 5px;
  opacity: 0.5 !important;
  border-radius: 0px 3px 3px 0px;
  transition: background-color 0.15s linear 0s;
}
</style>
<template>
  <v-container>
    <v-row dense>
      <v-col cols="12">
        <v-card class="info-card" flat>
          <v-card-subtitle>
            {{ text }}
          </v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      default: "",
    },
  },

  data() {
    return {}
  },
}
</script>
