// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github")
const darkCodeTheme = require("prism-react-renderer/themes/dracula")

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Dispatch - Documentation",
  tagline: "Incident Management for Everyone",
  favicon: "img/favicon.ico",

  // Set the production url of your site here
  url: "https://your-docusaurus-test-site.com",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "netflix", // Usually your GitHub org/user name.
  projectName: "dispatch", // Usually your repo name.
  trailingSlash: false,

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl: ({ docPath }) =>
            `https://github.com/netflix/dispatch/edit/master/docs/docs/${docPath}`,
        },
        //exclude: ["**/*.wip"],
        /*breadcrumbs: true,
        //lastVersion: "current",
        versions: {
          current: {
            label: "v2.x",
            badge: true,
            path: "latest",
          },
        },
        */
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: "img/docusaurus-social-card.jpg",
      navbar: {
        title: "Dispatch",
        logo: {
          alt: "Dispatch Logo",
          src: "img/logo.svg",
        },
        items: [
          { to: "/docs/user-guide/introduction", label: "User Guide", position: "left" },
          { to: "/docs/administration/introduction", label: "Administration", position: "left" },
          {
            to: "/docs/changelog",
            label: "What's New",
            position: "left",
          },
          {
            type: "docsVersionDropdown",
            position: "right",
            dropdownActiveClassDisabled: true,
            dropdownItemsAfter: [
              {
                href: "https://hasura.io/docs/1.0/graphql/core/index.html",
                label: "v1.x",
              },
            ],
          },
          {
            href: "https://github.com/Netflix/dispatch",
            label: "GitHub",
            position: "right",
          },
        ],
      },
      footer: {
        style: "dark",
        links: [],
        copyright: `Copyright © ${new Date().getFullYear()} Dispatch Documentation Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
}

module.exports = config
