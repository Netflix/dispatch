<template>
  <v-text-field :label="label" v-model="icon">
    <template #append>
      <v-menu v-model="menu" location="top" :close-on-content-click="false">
        <template #activator="{ props }">
          <div :style="swatchStyle" v-bind="props">
            <v-icon
              :icon="prepended(icon)"
              style="margin-top: 3px; margin-left: 3px"
              color="white"
            />
          </div>
        </template>
        <v-card>
          <v-card-text class="pa-0">
            <div>
              <div>
                <div>
                  <label for="iconSearch" style="display: none">Search for Icon</label>
                  <input
                    id="iconSearch"
                    placeholder="Search for Icon"
                    v-model="searchText"
                    @input="searchTextChanged"
                  />
                </div>
              </div>
              <div>
                <h4 class="icon-title">Regular Icons</h4>

                <ul v-if="allIcons.length > 0">
                  <li v-for="iconName in allIcons" :key="iconName">
                    <v-btn @click="selectIcon(iconName)">
                      <div class="text-center">
                        <v-icon :icon="prepended(iconName)" />
                        {{ iconName }}
                      </div>
                    </v-btn>
                  </li>
                </ul>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-menu>
    </template>
  </v-text-field>
</template>

<script>
import materialIcons from "../assets/icons"

export default {
  name: "IconPickerInput",

  props: {
    modelValue: {
      type: String,
      default: null,
    },
    label: {
      type: String,
      default: function () {
        return "Icon"
      },
    },
    color: {
      type: String,
      default: function () {
        return "#1976D2FF"
      },
    },
  },

  data() {
    return {
      menu: false,
      allIcons: [],
      searchText: "",
      loading: true,
      searchIconNotFound: false,
    }
  },

  methods: {
    selectIcon(icon) {
      this.menu = false
      this.$emit("update:modelValue", icon)
    },
    searchTextChanged() {
      this.searchIcon(this.searchText)
    },
    setDefaultIcons() {
      // get the names attribute from the list of allIcons
      this.allIcons = materialIcons.map((icon) => icon.name).slice(0, 10)
    },
    searchIcon(txt) {
      this.loading = true
      if (txt && txt.length > 0) {
        setTimeout(() => {
          this.loading = false
        }, 950)

        txt = txt.toLowerCase()
        this.allIcons = materialIcons
          .map((icon) => icon.name)
          .filter((icon) => icon.toLowerCase().includes(txt))
      } else {
        setTimeout(() => {
          this.setDefaultIcons()
          this.loading = false
        }, 950)
      }
    },
    prepended(icon) {
      return icon ? `mdi-${icon}` : ""
    },
  },
  created() {
    this.setDefaultIcons()
  },

  computed: {
    icon: {
      get() {
        return this.modelValue || null
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
    swatchStyle() {
      return {
        // set the color to the color prop
        backgroundColor: this.color || "#000000",
        cursor: "pointer",
        height: "30px",
        width: "30px",
        borderRadius: "4px",
        transition: "border-radius 200ms ease-in-out",
      }
    },
  },
}
</script>
