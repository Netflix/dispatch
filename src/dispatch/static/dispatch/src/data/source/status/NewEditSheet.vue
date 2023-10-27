<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer
      v-model="showCreateEdit"
      location="right"
      width="800"
      :permanent="$vuetify.display.mdAndDown"
    >
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Status</v-list-item-subtitle>

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
            <v-btn icon variant="text" color="secondary" @click="closeCreateEdit">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
        </v-list-item>
        <v-card>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="name"
                    label="Name"
                    hint="Name of status."
                    clearable
                    required
                    name="Name"
                    :rules="[rules.required]"
                  />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="description"
                    label="Description"
                    hint="Description of status."
                    clearable
                    required
                    name="Description"
                    :rules="[rules.required]"
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
      </template>
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
  name: "SourceStatusNewEditSheet",

  computed: {
    ...mapFields("sourceStatus", [
      "selected.project",
      "selected.id",
      "selected.name",
      "selected.description",
      "selected.loading",
      "dialogs.showCreateEdit",
    ]),
  },

  methods: {
    ...mapActions("sourceStatus", ["closeCreateEdit"]),
    save() {
      const self = this
      this.$store.dispatch("sourceStatus/save").then(function (data) {
        self.$emit("new-source-status-created", data)
      })
    },
  },

  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
  },
}
</script>
