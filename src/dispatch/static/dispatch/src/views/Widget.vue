<template>
  <div id="page-lists">
    <v-container fluid>
      <v-row>
        <v-col lg="4">
          <profile-card />
        </v-col>
        <v-col lg="4">
          <menu-card />
        </v-col>
        <v-col lg="4">
          <setting-card />
        </v-col>
      </v-row>
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
    SettingCard,
  },
  data() {
    return {}
  },
  computed: {},
  methods: {},
}
</script>
