<template>
  <v-combobox
    label="Members"
    :items="value.suggestedMembers"
    chips
    multiple
    clearable
    :allow-overflow="false"
    :loading="isLoading"
    item-text="content.name"
    :return-object="true"
    :search-input.sync="search"
    no-filter
    @input="addMembers($event)"
    @update:search-input="setFilterOptions({ q: $event })"
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
      default: null
    }
  },
  data() {
    return {
      search: ""
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
      }
    }
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
    setFilterOptions: debounce(function() {}, 200)
  }
}
</script>
