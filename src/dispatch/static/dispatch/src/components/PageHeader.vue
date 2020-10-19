<template>
  <v-layout class="align-center layout px-4 pt-4 app--page-header">
    <div class="page-header-left">
      <h3 class="pr-3">
        {{ $route.meta.title || "" }}
      </h3>
    </div>
    <v-breadcrumbs divider="/" :items="breadcrumbs">
      <template v-slot:item="props">
        <router-link :to="props.item.href" :class="[props.item.disabled && 'disabled']">
          {{ props.item.text }}
        </router-link>
      </template>
    </v-breadcrumbs>
    <v-spacer />
    <div class="page-header-right">
      <v-btn icon @click="refresh">
        <v-icon class="text--secondary">
          refresh
        </v-icon>
      </v-btn>
    </div>
  </v-layout>
</template>

<script>
export default {
  data() {
    return {
      title: "Home",
      breadcrumbs: []
    }
  },
  watch: {
    "$route.path": function() {
      this.computeBreadcrumbs()
    }
  },
  created() {
    this.computeBreadcrumbs()
  },
  methods: {
    refresh() {
      this.$router.go()
    },
    computeBreadcrumbs() {
      let breadcrumbs = [
        {
          text: "Home",
          href: "/",
          disabled: false
        }
      ]
      let appends = []
      appends = this.$route.matched.map(item => {
        return {
          text: item.meta.title || "",
          href: item.path || "/",
          disabled: item.path === this.$route.path
        }
      })
      this.breadcrumbs = breadcrumbs.concat(appends)
    }
  }
}
</script>
<style lang="stylus" scoped>
.disabled {
  color: grey;
  pointer-events: none;
  text-decoration: blink;
}
</style>
