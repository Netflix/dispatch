<template>
    <div class="text-box">
      <div ref="backdrop" class="backdrop">
        <div class="matches" v-html="matches"></div>
      </div>
      <v-textarea ref="text" v-model="text" placeholder="Enter text to check matches" @scroll="handleScroll"/>
    </div>
  </template>

  <script>
  import { mapMutations, mapGetters } from 'vuex';
  export default {
    name: "TextArea",
    data() {
      return {
        text: ''
      };
    },
    computed: mapGetters(['matches']),
    watch: {
      text(value) {
        this.updateText(value);
        this.handleScroll();
      }
    },
    methods: {
      ...mapMutations(['updateText']),
      handleScroll() {
        this.$refs.backdrop.scrollTop = this.$refs.text.scrollTop;
      }
    }
  };
  </script>
  <style>
