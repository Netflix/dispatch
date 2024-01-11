module.exports = {
  root: true,
  plugins: ["eslint-plugin-local-rules", "@typescript-eslint"],
  extends: [
    "eslint:recommended",
    "plugin:prettier/recommended",
    "plugin:vue/vue3-strongly-recommended",
    "plugin:vuetify/base",
  ],
  parserOptions: {
    ecmaVersion: 2020,
    parser: "@typescript-eslint/parser",
  },
  env: {
    browser: true,
    es2021: true,
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
    // "local-rules/list-item-children": "error",
    // "local-rules/vee-validate": "error",

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
    "vue/require-explicit-emits": "off",
    "vuetify/no-deprecated-components": "off",
  },
}
