<template>
  <v-layout wrap>
    <new-edit-sheet />
    <delete-dialog />
    <div class="headline">
      Policies
    </div>
    <v-spacer />
    <v-btn color="primary" dark class="mb-2" @click="createPolicy()">
      New
    </v-btn>
    <v-flex xs12>
      <v-layout column>
        <v-flex>
          <v-card>
            <v-card-title>
              <v-text-field
                :value="filterOptions.q"
                append-icon="search"
                label="Search"
                single-line
                hide-details
                clearable
                :loading="isLoading"
                @input="setFilterOptions({ q: $event })"
              />
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="policies.items"
              :server-items-length="policies.total"
              @update:options="setFilterOptions($event)"
            >
              <template v-slot:item.actions="{ item }">
                <v-icon small class="mr-2" @click="editPolicy(item)">
                  edit
                </v-icon>
                <v-icon small @click="deletePolicy(item)">
                  delete
                </v-icon>
              </template>
            </v-data-table>
          </v-card>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
import { debounce } from "lodash"
import { mapState, mapActions, mapMutations } from "vuex"
import NewEditSheet from "@/policy/NewEditSheet.vue"
import DeleteDialog from "@/policy/DeleteDialog.vue"
export default {
  name: "PolicyTable",
  components: {
    NewEditSheet,
    DeleteDialog
  },
  data() {
    return {
      headers: [
        { text: "Name", value: "name" },
        { text: "Description", value: "description", sortable: false },
        { text: "Expression", value: "expression", sortable: false },
        { text: "Actions", value: "actions", sortable: false }
      ]
    }
  },

  computed: {
    ...mapState("policy", ["policies", "isLoading", "filterOptions"])
  },
  created() {
    this.$store.dispatch("policy/getPolicies")
  },

  methods: {
    ...mapActions("policy", ["getPolicies", "selectPolicy", "showNewEditSheet"]),
    ...mapMutations("policy", ["SET_POLICIES", "SELECT_POLICIES"]),
    createPolicy() {
      this.$store.dispatch("policy/showNewEditSheet", true)
    },
    editPolicy(policy) {
      this.$store.dispatch("policy/selectPolicy", policy)
      this.$store.dispatch("policy/showNewEditSheet", true)
    },
    deletePolicy(policy) {
      this.$store.dispatch("policy/selectPolicy", policy)
      this.$store.dispatch("policy/showDeleteDialog", true)
    },
    setFilterOptions: debounce(function(options) {
      this.$store.dispatch("policy/setFilterOptions", options)
    }, 200)
  }
}
</script>
