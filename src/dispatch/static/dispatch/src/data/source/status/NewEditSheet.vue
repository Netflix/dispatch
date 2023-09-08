<template>
  <v-form @submit.prevent v-slot="{ isValid }">
    <v-navigation-drawer
      v-model="showCreateEdit"
      app
      clipped
      location="right"
      width="800"
      :permanent="$vuetify.display.mdAndDown"
    >
      <template #prepend>
        <v-list-item lines="two">
          <v-list-item-title v-if="id" class="text-h6"> Edit </v-list-item-title>
          <v-list-item-title v-else class="text-h6"> New </v-list-item-title>
          <v-list-item-subtitle>Status</v-list-item-subtitle>

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
          <v-btn icon variant="text" color="secondary" @click="closeCreateEdit">
            <v-icon>close</v-icon>
          </v-btn>
        </v-list-item>
        <v-card flat>
          <v-card-text>
            <v-container grid-list-md>
              <v-layout wrap>
                <v-flex xs12>
                  <v-text-field
                    v-model="name"
                    label="Name"
                    hint="Name of status."
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
                    hint="Description of status."
                    clearable
                    required
                    name="Description"
                    :rules="[rules.required]"
                  />
                </v-flex>
              </v-layout>
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
