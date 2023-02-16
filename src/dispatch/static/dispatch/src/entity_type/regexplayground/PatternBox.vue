<template>
    <div class="pattern-box-wrapper">
      <v-text-field
          v-model="pattern"
          class="pattern-box"
          slot-scope="{ errors, valid }"
          :error-messages="errors"
          :success="valid"
          model-value="Enter pattern"
          label="Pattern"
          hint="The field where the entity will be present. Support JSON Path expressions."
          clearable
        />
      <p v-show="error" class="error-text">{{ error }}</p>
    </div>
  </template>

  <script>
  import { mapMutations } from 'vuex';
  export default {
    name: "PatternBox",
    data() {
      return {
        pattern: '',
        error: ''
      };
    },
    watch: {
      pattern(value) {
        try {
          new RegExp(value);
          this.updatePattern(value);
          this.error = '';
        } catch (error) {
          this.error = 'Expression is invalid';
        }
      }
    },
    methods: mapMutations(['updatePattern'])
  };
  </script>
