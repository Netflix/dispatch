<template>
  <div id="page-lists">
    <v-container grid-list-lg fluid>
      <v-layout row wrap>
        <v-flex lg4>
          <profile-card />
        </v-flex>
        <v-flex lg4>
          <menu-card />
        </v-flex>
        <v-flex lg4>
          <setting-card />
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import ProfileCard from "@/components/widgets/card/ProfileCard"
import MenuCard from "@/components/widgets/card/MenuCard"
import SettingCard from "@/components/widgets/card/SettingCard"
export default {
  components: {
    ProfileCard,
    MenuCard,
    SettingCard
  },
  data() {
    return {}
  },
  computed: {},
  methods: {}
}
</script>
