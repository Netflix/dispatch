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
  watch: {
    value(value) {
      if (this.editor.getValue() !== JSON.stringify(value, null, 2)) {
        this.editor.setValue(JSON.stringify(value, null, 2))
        this.editor.renderer.updateFull()
      }
    }
  },
  mounted() {
    this.editor = ace.edit("advancedEditor")
    this.session = this.editor.getSession()
    this.session.setMode("ace/mode/json")
    this.editor.setTheme("ace/theme/github")

    this.editor.on("change", () => {
      try {
        var o = JSON.parse(this.editor.getValue())

        if (o && typeof o === "object") {
          this.$emit("input", o)
        }
      } catch (e) {
        return false
      }
    })
  }
}
</script>
