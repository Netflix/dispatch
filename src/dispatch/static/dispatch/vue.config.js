const path = require("path")
const webpack = require("webpack")

function resolve(dir) {
  return path.join(__dirname, dir)
}

// vue.config.js
module.exports = {
  configureWebpack: {
    plugins: [
      // Ignore all locale files of moment.js
      new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
    ],
    devtool: "source-map"
  },

  chainWebpack: config => {
    config.resolve.alias.set("@$", resolve("src")).set("@views", resolve("src/views"))
  },

  css: {
    loaderOptions: {
      less: {
        modifyVars: {},
        javascriptEnabled: true
      }
    }
  },

  devServer: {
    // https://github.com/chimurai/http-proxy-middleware#http-proxy-options
    proxy: {
      "^/api": {
        target: "http://localhost:8000",
        ws: false,
        changeOrigin: true
      }
    },
    historyApiFallback: true,
    overlay: {
      warnings: false,
      errors: true
    }
  },

  assetsDir: "static",
  runtimeCompiler: true
}
