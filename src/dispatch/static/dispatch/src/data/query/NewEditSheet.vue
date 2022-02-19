<template>
  <ValidationObserver v-slot="{ invalid, validated }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped right width="600">
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-content>
            <v-list-item-title v-if="id" class="title"> Edit </v-list-item-title>
            <v-list-item-title v-else class="title"> New </v-list-item-title>
            <v-list-item-subtitle>Query</v-list-item-subtitle>
          </v-list-item-content>
          <v-btn
            icon
            color="info"
            :loading="loading"
            :disabled="invalid || !validated"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon color="secondary" @click="closeCreateEdit">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-tabs>
        <v-tab> Basic Info </v-tab>
        <v-tab> Text </v-tab>
        <v-tab-item>
          <edit-basic-info-tab />
        </v-tab-item>
        <v-tab-item>
          <edit-text-tab />
        </v-tab-item>
      </v-tabs>
    </v-navigation-drawer>
  </ValidationObserver>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import { ValidationObserver } from "vee-validate"

import EditBasicInfoTab from "@/data/query/EditBasicInfoTab.vue"
import EditTextTab from "@/data/query/EditTextTab.vue"

export default {
  name: "QueryNewEditSheet",

  components: {
    EditBasicInfoTab,
    EditTextTab,
    ValidationObserver,
  },

  computed: {
    ...mapFields("query", ["selected.id", "selected.loading", "dialogs.showCreateEdit"]),
  },

  methods: {
    ...mapActions("query", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("query/save").then(function (data) {
        self.$emit("new-query-created", data)
      })
    },
  },
}
</script>
