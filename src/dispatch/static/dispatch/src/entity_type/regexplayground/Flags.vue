<template>
    <div class="flags">
        <div class="input-group">
            <label for="global_match">
                <input type="checkbox" value="g" v-model="flags" id="global_match"> global match
            </label>
        </div>

        <div class="input-group">
            <label for="ignore_case">
                <input type="checkbox" value="i" v-model="flags" id="ignore_case"> case insensitive
            </label>
        </div>

    </div>
</template>

<script>
import { mapMutations } from 'vuex';
export default {
  name: "Flags",
  data() {
    return {
      flags: this.$store.getters.flags.split('')
    };
  },
  watch: {
    flags(update) {
      this.updateFlags(update.join(''));
    }
  },
  methods: mapMutations(['updateFlags'])
};
</script>

<style scoped>
.flags {
  display: flex;
  border-top: 1px solid #f7f7f72d;
  padding: 0.8rem;
  color: #d6d7cc;
}
.input-group {
  margin-right: 1.2rem;
  font-size: 12px;
}
</style>
