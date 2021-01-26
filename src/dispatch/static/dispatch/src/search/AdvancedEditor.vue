<template>
  <div id="advancedEditor" style="width: 100%; height: 100%;"></div>
</template>

<script>
import ace from "ace-builds/src-noconflict/ace"
import "ace-builds/src-noconflict/mode-json"
import "ace-builds/src-noconflict/theme-github"
import "ace-builds/webpack-resolver"

export default {
  name: "AdvancedEditor",
  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    }
  },
  computed: {
    content: {
      get() {
        return JSON.stringify(this.value, null, 2)
      },
      set(value) {
        try {
          var o = JSON.parse(value)

          // create our filter query

          if (o && typeof o === "object") {
            this.$emit("input", o)
          }
        } catch (e) {
          return false
        }
      }
    }
  },
  watch: {
    content(value) {
      this.editor.setValue(value, 1)
    }
  },
  mounted() {
    this.editor = ace.edit("advancedEditor")
    this.session = this.editor.getSession()
    this.editor.setValue(this.content, 1)

    this.session.setMode("ace/mode/json")
    this.editor.setTheme("ace/theme/github")

    this.editor.on("change", () => {
      this.content = this.editor.getValue()
    })
  }
}
</script>
