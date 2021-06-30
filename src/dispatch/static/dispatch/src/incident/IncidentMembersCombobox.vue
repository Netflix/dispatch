<template>
  <v-combobox
    deletable-chips
    :allow-overflow="false"
    :items="value.suggestedMembers"
    :loading="isLoading"
    :return-object="true"
    :search-input.sync="search"
    @input="addMembers($event)"
    @update:search-input="setFilterOptions({ q: $event })"
    chips
    clearable
    item-text="content.name"
    label="Members"
    multiple
    no-filter
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No Members matching "
            <strong>{{ search }}</strong
            >". Press <kbd>enter</kbd> to add.
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:selection="data">
      <v-chip close class="chip--select-multi" @input="removeMember($event)">
        {{ data.item.content.name }}
      </v-chip>
    </template>
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title>
          <div class="text-uppercase text-truncate">
            {{ data.item.content.name }}
          </div>
        </v-list-item-title>
        <v-list-item-subtitle>
          <div class="text-truncate">
            {{ data.item.type }}
          </div>
        </v-list-item-subtitle>
      </v-list-item-content>
    </template>
  </v-combobox>
</template>

<script>
import { debounce } from "lodash"
import { mapState, mapActions, mapMutations } from "vuex"
export default {
  name: "IncidentMemberCombobox",
  props: {
    value: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      search: "",
    }
  },

  computed: {
    ...mapState("route", ["results", "isLoading"]),
    ...mapState("incident", ["description"]),
    text: {
      set(text) {
        this.$store.dispatch("route/setText", text)
      },
      get() {
        return this.$store.state.text
      },
    },
  },

  components: {},

  methods: {
    ...mapActions("term", ["getMembers", "selectMember"]),
    ...mapMutations("term", ["SET_TERMS", "SELECT_TERM"]),
    addMembers(payload) {
      this.search = ""
      this.$emit("addMembers", payload)
    },
    removeMember(payload) {
      this.$emit("removeMember", payload)
    },
    setFilterOptions: debounce(function () {}, 500),
  },
}
</script>
