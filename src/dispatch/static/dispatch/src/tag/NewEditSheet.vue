<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer v-model="showCreateEdit" location="right" width="500">
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Tag</v-list-item-subtitle>

          <template #append>
            <v-btn
              icon
              variant="text"
              color="info"
              :loading="loading"
              :disabled="!isValid.value"
              @click="save()"
            >
              <v-icon>mdi-content-save</v-icon>
            </v-btn>
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit()">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </template>
      <v-card>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <span class="text-subtitle-2">Details</span>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="name"
                  label="Name"
                  hint="A name for your tag."
                  clearable
                  required
                  name="name"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="description"
                  label="Description"
                  hint="A description for your tag."
                  clearable
                  required
                  name="description"
                />
              </v-col>
              <v-col cols="12">
                <tag-type-select :project="project" v-model="tag_type" />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="source"
                  label="Source"
                  hint="The tag's source."
                  clearable
                  required
                  name="source"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="uri"
                  label="URI"
                  hint="The tag's URI."
                  clearable
                  required
                  name="uri"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="external_id"
                  label="External ID"
                  hint="A tags external id."
                  clearable
                  name="external_id"
                />
              </v-col>
              <v-col>
                <v-checkbox
                  v-model="discoverable"
                  label="Discoverable"
                  hint="Is this tag a common word or is it eligible for auto-detection?"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
  </v-form>
</template>

<script>
import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import TagTypeSelect from "@/tag_type/TagTypeSelect.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "TagNewEditSheet",

  components: {
    TagTypeSelect,
  },

  computed: {
    ...mapFields("tag", [
      "selected.name",
      "selected.id",
      "selected.tag_type",
      "selected.uri",
      "selected.description",
      "selected.source",
      "selected.project",
      "selected.discoverable",
      "selected.external_id",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("tag", ["save", "closeCreateEdit"]),
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
