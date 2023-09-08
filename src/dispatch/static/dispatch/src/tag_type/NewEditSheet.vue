<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" app clipped location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Tag Type</v-list-item-subtitle>

          <v-btn
            icon
            variant="text"
            color="info"
            :loading="loading"
            :disabled="!isValid.value"
            @click="save()"
          >
            <v-icon>save</v-icon>
          </v-btn>
          <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
      </template>
      <v-card flat>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12>
                <span class="text-subtitle-2">Details</span>
              </v-flex>
              <v-flex xs12>
                <v-text-field
                  v-model="name"
                  label="Name"
                  hint="A name for your tag type."
                  clearable
                  required
                  name="Name"
                  :rules="[rules.required]"
                />
              </v-flex>
              <v-flex xs12>
                <v-textarea
                  v-model="description"
                  label="Description"
                  hint="A description for your tag type."
                  clearable
                  required
                  name="Description"
                />
              </v-flex>
              <v-flex>
                <v-checkbox
                  v-model="exclusive"
                  label="Exclusive"
                  hint="Should an incident only have one tag of this type?"
                />
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "TagTypeNewEditSheet",

  computed: {
    ...mapFields("tag_type", [
      "dialogs.showCreateEdit",
      "selected.id",
      "selected.name",
      "selected.project",
      "selected.description",
      "selected.exclusive",
      "selected.loading",
    ]),
    ...mapFields("tag_type", {
      default_tag_type: "selected.default",
    }),
  },

  methods: {
    ...mapActions("tag_type", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
