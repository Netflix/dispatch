import "./VCircle.styl"
import Colorable from "vuetify/es5/mixins/colorable"
export default {
  mixins: [Colorable],

  props: {
    text: String,
    small: Boolean,
    large: Boolean,
    medium: Boolean,
    dot: Boolean,
    pill: Boolean,
    ring: Boolean
  },
  computed: {
    classes() {
      const classes = {
        "circle-sm": this.small,
        "circle-lg": this.medium,
        "circle-xl": this.large,
        "circle-ring": this.ring,
        "circle-dot": this.dot,
        "circle-pill": this.pill,
        "theme--light": this.light,
        "theme--dark": this.dark
      }
      return classes
    }
  },
  render(h) {
    const data = {
      staticClass: "circle",
      class: this.classes,
      attrs: { tabindex: this.disabled ? -1 : 0 },
      on: this.$listeners
    }

    return h("span", data, [this.$slots.default])
  }
}
