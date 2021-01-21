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
      type: Object,
      default: function() {
        return {}
      }
    }
  },
  computed: {
    content: {
      get() {
        return JSON.stringify(this.value)
      },
      set(value) {
        this.$emit("input", JSON.parse(value))
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
    this.editor.setValue(JSON.stringify(this.content), 1)

    this.editor.getSession().setMode("ace/mode/json")
    this.editor.setTheme("ace/theme/github")

    this.editor.on("change", () => {
      this.content = this.editor.getValue()
    })
  }
}
</script>
