<template>
  <v-combobox
    closable-chips
    :allow-overflow="false"
    :items="value.suggestedMembers"
    :loading="isLoading"
    :return-object="true"
    v-model:search="search"
    @update:model-value="addMembers($event)"
    @update:search="setFilterOptions({ q: $event })"
    chips
    clearable
    item-title="content.name"
    label="Members"
    multiple
    no-filter
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No Members matching "
          <strong>{{ search }}</strong
          >". Press <kbd>enter</kbd> to add.
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #selection="data">
      <v-chip closable class="chip--select-multi" @update:model-value="removeMember($event)">
        {{ data.item.content.name }}
      </v-chip>
    </template>
    <template #item="data">
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
