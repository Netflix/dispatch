<template>
  <v-navigation-drawer :value="showNewEditSheet" app clipped right width="500">
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-content>
          <v-list-item-title v-if="selectedPolicy.id" class="title">
            Edit
          </v-list-item-title>
          <v-list-item-title v-else class="title">
            New
          </v-list-item-title>
          <v-list-item-subtitle>Term</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
    <v-card flat>
      <v-card-text>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <v-text-field
                :value="selectedPolicy.name"
                label="Name"
                @input="updateSelectedPolicy({ name: $event })"
              />
            </v-flex>
            <v-flex xs12>
              <v-textarea
                :value="selectedPolicy.expression"
                label="Expression"
                @input="updateSelectedPolicy({ expression: $event })"
              />
            </v-flex>
            <v-flex xs12>
              <v-textarea
                :value="selectedPolicy.description"
                label="Description"
                @input="updateSelectedPolicy({ description: $event })"
              />
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="blue darken-1" text @click="close">
          Cancel
        </v-btn>
        <v-btn color="blue darken-1" text @click="performSave(selectedPolicy)">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { mapState, mapActions } from "vuex"
export default {
  name: "PolicyNewEditDialog",

  components: {},

  computed: {
    ...mapState("policy", ["selectedPolicy", "showNewEditSheet"])
  },

  methods: {
    ...mapActions("policy", [
      "createPolicy",
      "updatePolicy",
      "addTerm",
      "removeTerm",
      "updateSelectedPolicy"
    ]),

    close() {
      this.$store.dispatch("policy/showNewEditSheet", false)
    },

    performSave(policy) {
      if (!this.selectedPolicy.id) {
        this.$store.dispatch("policy/createPolicy", policy)
      } else {
        this.$store.dispatch("policy/updatePolicy", policy)
      }
    },

    addTerms(term) {
      this.$store.dispatch("policy/addSelectedPolicyTerms", term)
    },
    removeTerm(term) {
      this.$store.dispatch("policy/removeSelectedPolicyTerm", term)
    }
  }
}
</script>
