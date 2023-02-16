<template>
    <div>
      <div class="regex-box">
        <div class="main">
          <pattern-box></pattern-box>
          <text-area></text-area>
        </div>
      </div>
    </div>
  </template>

  <script>
  import TextArea from '@/entity_type/regexplayground/TextArea.vue';
  import PatternBox from '@/entity_type/regexplayground/PatternBox.vue';

  export default {
    name: "RegexBox",
    components: {
      TextArea,
      PatternBox
    }
  };
  </script>
