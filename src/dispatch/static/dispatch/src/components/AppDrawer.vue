<template>
  <v-navigation-drawer app :value="toggleDrawer" clipped>
    <vue-perfect-scrollbar class="drawer-menu--scroll" :settings="scrollSettings">
      <v-list dense>
        <template v-for="item in menus">
          <!--group with subitems-->
          <v-list-group
            v-if="item.items"
            :key="item.title"
            :group="item.group"
            :prepend-icon="item.icon"
            no-action="no-action"
          >
            <v-list-item slot="activator" ripple="ripple">
              <v-list-item-content>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <template v-for="subItem in item.items">
              <!--sub group-->
              <v-list-group
                v-if="subItem.items"
                :key="subItem.name"
                :group="subItem.group"
                sub-group="sub-group"
              >
                <v-list-item slot="activator" ripple="ripple">
                  <v-list-item-content>
                    <v-list-item-title>{{ subItem.title }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item
                  v-for="grand in subItem.children"
                  :key="grand.name"
                  to="genChildTarget(item, grand)"
                  ripple="ripple"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ grand.title }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-group>
              <!--child item-->
              <v-list-item
                v-else
                :key="subItem.name"
                :to="genChildTarget(item, subItem)"
                :disabled="subItem.disabled"
                :target="subItem.target"
                ripple="ripple"
                exact
              >
                <v-list-item-content>
                  <v-list-item-title>
                    <span>{{ subItem.title }}</span>
                  </v-list-item-title>
                </v-list-item-content>
                <v-list-item-action v-if="subItem.action">
                  <v-icon :class="[subItem.actionClass || 'success--text']">
                    {{ subItem.action }}
                  </v-icon>
                </v-list-item-action>
              </v-list-item>
            </template>
          </v-list-group>
          <v-subheader v-else-if="item.header" :key="item.name">
            {{ item.header }}
          </v-subheader>
          <v-divider v-else-if="item.divider" :key="item.name" />
          <!--top-level link-->
          <v-list-item
            v-else
            :key="item.name"
            :to="item.href"
            ripple="ripple"
            :disabled="item.disabled"
            :target="item.target"
            rel="noopener"
            exact
          >
            <v-list-item-action v-if="item.icon">
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action v-if="item.subAction">
              <v-icon class="success--text">
                {{ item.subAction }}
              </v-icon>
            </v-list-item-action>
          </v-list-item>
        </template>
      </v-list>
    </vue-perfect-scrollbar>
  </v-navigation-drawer>
</template>
<script>
import menu from "@/api/menu"
import { mapState } from "vuex"
import VuePerfectScrollbar from "vue-perfect-scrollbar"
export default {
  name: "AppDrawer",
  components: {
    VuePerfectScrollbar
  },
  props: {
    expanded: {
      type: Boolean,
      default: true
    },
    drawWidth: {
      type: [Number, String],
      default: "260"
    }
  },
  data() {
    return {
      menus: menu,
      scrollSettings: {
        maxScrollbarLength: 160
      }
    }
  },
  computed: {
    computeLogo() {
      return "/static/m.png"
    },
    ...mapState("app", ["toggleDrawer"])
  },
  created() {},

  methods: {
    genChildTarget(item, subItem) {
      if (subItem.href) return
      if (subItem.component) {
        return {
          name: subItem.component
        }
      }
      return { name: `${item.group}/${subItem.name}` }
    }
  }
}
</script>
