<template>
  <div>
    <!-- Use the component in the right place of the template -->
    <tiptap-vuetify
      v-model="content"
      :extensions="extensions"
      :card-props="{ flat: true, color: 'grey lighten-5', rounded: true }"
    />
  </div>
</template>

<script>
// import the component and the necessary extensions
import {
  TiptapVuetify,
  Heading,
  Bold,
  Italic,
  Underline,
  Code,
  Paragraph,
  BulletList,
  OrderedList,
  ListItem,
  Link,
  Blockquote,
  HardBreak,
  HorizontalRule,
  History,
} from "tiptap-vuetify"

export default {
  name: "RichEditor",
  // specify TiptapVuetify component in "components"
  components: { TiptapVuetify },
  data: () => ({
    // declare extensions you want to use
    extensions: [
      Bold,
      Italic,
      ListItem,
      BulletList,
      OrderedList,
      Blockquote,
      Link,

      Code,
      HardBreak,
    ],
    // starting editor's content
    content: `
      <blockquote>Document your findings and provide the rationale for any decisions you made as part of this investigation...</blockquote>
      <br></br>
      <br></br>
    `,
  }),
}
</script>
