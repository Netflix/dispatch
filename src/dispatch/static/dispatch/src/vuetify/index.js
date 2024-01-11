import "@mdi/font/css/materialdesignicons.css"
import "vuetify/styles"
import { createVuetify } from "vuetify"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"

export function vuetifyPlugin(app) {
  const vuetify = createVuetify({
    defaults: {
      VTextField: {
        variant: "underlined",
      },
      VTextarea: {
        variant: "underlined",
      },
      VSelect: {
        variant: "underlined",
        itemTitle: "text",
      },
      VAutocomplete: {
        variant: "underlined",
        itemTitle: "text",
      },
      VCombobox: {
        variant: "underlined",
        itemTitle: "text",
      },
      VExpansionPanel: {
        elevation: 0,
      },
      VCheckbox: {
        color: "primary",
      },
      VRadioGroup: {
        color: "primary",
      },
      VSwitch: {
        color: "primary",
      },
      VProgressLinear: {
        color: "primary",
      },
      VIcon: {
        color: "#616161",
      },
      VDataTable: {
        hover: true,
        VSelect: {
          itemTitle: "title",
        },
      },
      VDataTableServer: {
        hover: true,
        VSelect: {
          itemTitle: "title",
        },
      },
    },
    components: {
      ...components,
    },
    directives,
    theme: {
      themes: {
        light: {
          colors: {
            primary: "#E50914",
            secondary: "#404041",
            accent: "#8c9eff",
            anchor: "#0F0F0F",
            error: "#E50914",
            exception: "#E50914",
            info: "#4969E4",
            warning: "#FBA404",
            success: "#41B957",
            toolbar: "#FFFFFF",
            background0: "#FFFFFF",
            background1: "#FAFAFA",
            background2: "#F0F0F0",
            gray0: "#0F0F0F",
            gray1: "#161616",
            gray2: "#232323",
            gray3: "#404041",
            gray4: "#6D6D6E",
            gray5: "#929292",
            gray6: "#B6B6B7",
            gray7: "#DEDEDE",
            gray8: "#F0F0F0",
            gray9: "#FAFAFA",
            white: "#FFFFFF",
          },
          variables: {
            borderline: "#E4E4E4",
          },
        },
        dark: {
          colors: {
            primary: "#E50914",
            secondary: "#B6B6B7",
            accent: "#8c9eff",
            error: "#E50914",
            exception: "#E50914",
            info: "#4969E4",
            warning: "#FBA404",
            success: "#41B957",
            toolbar: "#404041",
            background0: "#0F0F0F",
            background1: "#161616",
            background2: "#232323",
            gray0: "#0F0F0F",
            gray1: "#161616",
            gray2: "#232323",
            gray3: "#404041",
            gray4: "#6D6D6E",
            gray5: "#929292",
            gray6: "#B6B6B7",
            gray7: "#DEDEDE",
            gray8: "#F0F0F0",
            gray9: "#FAFAFA",
            white: "#FFFFFF",
          },
          variables: {
            borderline: "#404040",
          },
        },
      },
    },
  })

  app.use(vuetify)
}
