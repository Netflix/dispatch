const path = require("path")
const MonacoWebpackPlugin = require("monaco-editor-webpack-plugin")
const webpack = require("webpack")

function resolve(dir) {
  return path.join(__dirname, dir)
}

// vue.config.js
module.exports = {
  transpileDependencies: ["vuetify", "@koumoul/vjsf"],
  chainWebpack: (config) => {
    config.plugin("monaco-editor").use(MonacoWebpackPlugin, [
      {
        // Languages are loaded on demand at runtime
        languages: ["json"],
        features: ["find"],
      },
    ])
    config.resolve.alias.set("@$", resolve("src")).set("@views", resolve("src/views"))
  },
  configureWebpack: {
    plugins: [
      // Ignore all locale files of moment.js
      new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    ],
    devtool: "source-map",
  },
  css: {
    loaderOptions: {
      less: {
        modifyVars: {},
        javascriptEnabled: true,
      },
    },
  },

  devServer: {
    // https://github.com/chimurai/http-proxy-middleware#http-proxy-options
    proxy: {
      "^/api": {
        target: "http://127.0.0.1:8000",
        ws: false,
        changeOrigin: true,
      },
    },
    historyApiFallback: true,
    overlay: {
      warnings: false,
      errors: true,
    },
  },

  assetsDir: "static",
  runtimeCompiler: true,
}
