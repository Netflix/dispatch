module.exports = {
  root: true,
  plugins: ["eslint-plugin-local-rules"],
  extends: [
    "eslint:recommended",
    "plugin:prettier/recommended",
    "plugin:vue/vue3-strongly-recommended",
    "plugin:vuetify/base",
  ],
  parserOptions: {
    ecmaVersion: 2020,
  },
  env: {
    browser: true,
    node: true,
  },
  overrides: [
    {
      files: ["test/*"],
      rules: {
        "no-undef": "off",
      },
    },
  ],
  rules: {
    "local-rules/icon-button-variant": "error",

    // Conflicts with prettier
    "vue/max-attributes-per-line": "off",
    "vue/singleline-html-element-content-newline": "off",
    "vue/html-self-closing": [
      "warn",
      {
        html: {
          void: "any",
        },
      },
    ],
    "vue/html-closing-bracket-newline": "off",
    "vue/html-indent": "off",
    "vue/script-indent": "off",

    // Bad defaults
    "vue/valid-v-slot": [
      "error",
      {
        allowModifiers: true,
      },
    ],
    "vue/multi-word-component-names": "off",
    "vue/attribute-hyphenation": "off",
    "vue/require-default-prop": "off",
  },
}
