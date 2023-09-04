module.exports = {
  "icon-button-variant": {
    meta: {
      fixable: "code",
    },
    create(context) {
      const template = context.parserServices.getTemplateBodyTokenStore()

      return context.parserServices.defineTemplateBodyVisitor({
        VElement(node) {
          if (node.name !== "v-btn") return

          const attr = node.startTag.attributes.find((attr) => {
            return attr.type === "VAttribute" && attr.key.name === "icon"
          })
          if (
            attr &&
            !node.startTag.attributes.some((attr) => {
              return attr.type === "VAttribute" && attr.key.name === "variant"
            })
          ) {
            context.report({
              node: attr,
              message: 'default icon button variant is contained, override to variant="text"?',
              fix(fixer) {
                const tokenBefore = template.getTokenBefore(attr)
                if (attr.loc.start.line === tokenBefore.loc.start.line) {
                  return fixer.insertTextAfter(attr, ' variant="text"')
                } else if (attr.loc.start.line === tokenBefore.loc.start.line + 1) {
                  const indent = attr.loc.start.column
                  return fixer.insertTextAfter(attr, "\n" + " ".repeat(indent) + 'variant="text"')
                }
              },
            })
          }
        },
      })
    },
  },
}
