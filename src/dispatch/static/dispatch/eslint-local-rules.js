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
  "vee-validate": {
    meta: {
      fixable: "code",
    },
    create(context) {
      const template = context.parserServices.getTemplateBodyTokenStore()
      let observerNode
      let formNode
      let observerRefNodes = []
      const rulesToImport = new Set()
      const vvImportNodes = []
      const vvRuleImportNodes = []
      const validationProviderNodes = []
      let vueObjectNode
      let hasSetup = false
      const methodNodes = []

      return context.parserServices.defineTemplateBodyVisitor(
        {
          'VElement[parent.type!="VElement"]:exit'(node) {
            if (rulesToImport.size) {
              if (!vueObjectNode) {
                return context.report({
                  node: context.sourceCode.ast,
                  message: "unable to locate vue object",
                })
              }
              if (hasSetup) {
                return context.report({
                  node: vueObjectNode,
                  message: "component already has setup defined",
                })
              }
            }

            if (
              !(
                vvImportNodes.length ||
                vvRuleImportNodes.length ||
                observerNode ||
                validationProviderNodes.length ||
                rulesToImport.size
              )
            )
              return

            return context.report({
              node,
              message: "replace validation-observer with v-form",
              fix(fixer) {
                const fixes = []

                // remove vee-validate imports
                vvImportNodes.forEach((node) => {
                  fixes.push(fixer.remove(node))
                  context.getDeclaredVariables(node).forEach((variable) => {
                    variable.references.forEach((reference) => {
                      fixes.push(
                        fixer.removeRange([
                          context.sourceCode.getIndexFromLoc({
                            line: reference.identifier.parent.loc.start.line,
                            column: 0,
                          }) - 1,
                          context.sourceCode.getIndexFromLoc(reference.identifier.parent.loc.end) +
                            1,
                        ])
                      )
                    })
                  })
                })
                vvRuleImportNodes.forEach((node) => {
                  fixes.push(fixer.remove(node))
                })

                if (observerNode) {
                  const observerRef = observerNode.startTag.attributes.find((attr) => {
                    return attr.type === "VAttribute" && attr.key.name === "ref"
                  })
                  const observerSlot = observerNode.startTag.attributes.find((attr) => {
                    return (
                      attr.type === "VAttribute" &&
                      attr.key.type === "VDirectiveKey" &&
                      attr.key.name.name === "slot"
                    )
                  })
                  const otherAttrs = observerNode.startTag.attributes
                    .filter((attr) => {
                      return attr !== observerRef && attr !== observerSlot
                    })
                    .map((attr) => context.sourceCode.getText(attr))

                  let formSubmitHandlerName
                  let formSubmitHandlerNode
                  if (formNode) {
                    const submitListener = formNode.startTag.attributes.find((attr) => {
                      return (
                        attr.directive &&
                        attr.key.name.name === "on" &&
                        attr.key.argument.name === "submit"
                      )
                    })

                    if (submitListener) {
                      formSubmitHandlerName = submitListener.value.expression.name
                      if (formSubmitHandlerName) {
                        methodNodes.forEach((node) => {
                          if (node.key.name === formSubmitHandlerName) {
                            formSubmitHandlerNode = node
                          }
                        })
                        if (!formSubmitHandlerNode) {
                          throw new Error("Unable to locate form submit handler")
                        }
                      }
                    } else {
                      throw new Error("No submit listener")
                    }
                  }

                  let newStartTag = "<v-form"
                  if (observerRef) {
                    newStartTag += ` ref="form"`
                  }
                  if (otherAttrs.length) {
                    newStartTag += " " + otherAttrs.join(" ")
                  }
                  if (formNode) {
                    const formAttrs = formNode.startTag.attributes.map((attr) =>
                      context.sourceCode.getText(attr)
                    )
                    if (formAttrs.length) {
                      newStartTag += " " + formAttrs.join(" ")
                    }
                  } else {
                    newStartTag += ` @submit.prevent`
                  }
                  if (observerSlot) {
                    newStartTag += ` v-slot="{ isValid }"`
                  }
                  newStartTag += ">"

                  if (formNode) {
                    fixes.push(
                      fixer.replaceTextRange(
                        [observerNode.startTag.range[0], formNode.startTag.range[1]],
                        newStartTag
                      )
                    )
                  } else {
                    fixes.push(fixer.replaceText(observerNode.startTag, newStartTag))
                  }

                  if (observerSlot) {
                    observerNode.variables.forEach((variable) => {
                      if (variable.id.name === "invalid") {
                        variable.references.forEach((ref) => {
                          fixes.push(fixer.replaceText(ref.id, "!isValid.value"))
                        })
                      } else if (variable.id.name !== "validated") {
                        throw new Error("unsupported variable")
                      }
                    })
                  }

                  if (formNode) {
                    fixes.push(
                      fixer.replaceTextRange(
                        [formNode.endTag.range[0], observerNode.endTag.range[1]],
                        "</v-form>"
                      )
                    )
                  } else {
                    fixes.push(fixer.replaceText(observerNode.endTag, "</v-form>"))
                  }

                  observerRefNodes.forEach((node) => {
                    fixes.push(fixer.replaceText(node.property, "form"))
                    if (node.parent.property.name === "reset") {
                      fixes.push(fixer.replaceText(node.parent.property, "resetValidation"))
                    } else {
                      fixes.push({
                        range: Array(2).fill(
                          context.sourceCode.getIndexFromLoc({
                            line: node.loc.start.line + 1,
                            column: 0,
                          }) - 1
                        ),
                        text: " // TODO: find vuetify equivalent",
                      })
                    }
                  })

                  if (formSubmitHandlerNode) {
                    if (!formSubmitHandlerNode.value.async) {
                      fixes.push(fixer.insertTextBefore(formSubmitHandlerNode.key, "async "))
                    }
                    let paramName = "event"
                    if (!formSubmitHandlerNode.value.params.length) {
                      fixes.push(
                        fixer.replaceTextRange(
                          [
                            formSubmitHandlerNode.value.range[0],
                            formSubmitHandlerNode.value.body.range[0],
                          ],
                          `(${paramName}) `
                        )
                      )
                    } else {
                      paramName = formSubmitHandlerNode.value.params[0].name
                    }
                    const indent = context.sourceCode.lines
                      .at(formSubmitHandlerNode.value.body.body[0].loc.start.line - 1)
                      .match(/^\s*/)[0]
                    fixes.push(
                      fixer.insertTextBefore(
                        formSubmitHandlerNode.value.body.body[0],
                        `if (!(await ${paramName}).valid) return\n\n${indent}`
                      )
                    )
                  }
                }

                validationProviderNodes.forEach(({ node, child, rules, vid }) => {
                  fixes.push(fixer.removeRange([node.startTag.range[0], child.startTag.range[0]]))

                  if (node.variables.length) {
                    const b4 = template.getTokenBefore(
                      node.variables[0].references[0].id.parent.parent
                    )
                    fixes.push(
                      fixer.removeRange([
                        b4.range[1],
                        node.variables[0].references[0].id.parent.parent.range[1],
                      ])
                    )
                  } else {
                    node.children.forEach((child) => {
                      if (child.type === "VElement") {
                        child.startTag.attributes.forEach((attr) => {
                          if (
                            attr.key.type === "VDirectiveKey" &&
                            attr.key.name.name === "slot-scope"
                          ) {
                            fixes.push(fixer.remove(attr))
                            if (child.variables.length) {
                              child.variables.forEach((variable) => {
                                const b4 = template.getTokenBefore(
                                  variable.references[0].id.parent.parent
                                )
                                fixes.push(
                                  fixer.removeRange([
                                    b4.range[1],
                                    variable.references[0].id.parent.parent.range[1],
                                  ])
                                )
                              })
                            } else {
                              throw new Error("slot-scope without variables")
                            }
                          }
                        })
                      }
                    })
                  }

                  const isMultiline = child.startTag.loc.start.line !== child.startTag.loc.end.line
                  const indent = isMultiline
                    ? "\n" +
                      context.sourceCode.lines
                        .at(child.startTag.loc.start.line - 1)
                        .match(/^\s*/)[0] +
                      " ".repeat(2)
                    : " "

                  if (vid) {
                    fixes.push(
                      fixer.insertTextAfter(
                        child.startTag.attributes.at(-1),
                        indent +
                          (vid.directive
                            ? `:name=${context.sourceCode.getText(vid.value)}`
                            : `name="${vid.value.value}"`)
                      )
                    )
                  }
                  if (rules) {
                    let rulesArray
                    let rulesString
                    if (rules.directive) {
                      // dynamic rules
                      if (
                        rules.value.expression.type !== "TemplateLiteral" ||
                        rules.value.expression.quasis.length !== 2 ||
                        rules.value.expression.expressions.length !== 1 ||
                        rules.value.expression.expressions[0].type !== "ConditionalExpression" ||
                        rules.value.expression.expressions[0].alternate.type !== "Literal" ||
                        rules.value.expression.expressions[0].alternate.value !== ""
                      ) {
                        throw new Error("Unsupported dynamic rules")
                      }
                      const test = context.sourceCode.getText(
                        rules.value.expression.expressions[0].test
                      )
                      const rulesValue = rules.value.expression.expressions[0].consequent.value
                      rulesArray = rulesValue.split("|")
                      rulesString = `:rules="${test} ? [${rulesArray
                        .map((v) => `rules.${v}`)
                        .join(", ")}] : []"`
                    } else {
                      const rulesValue = rules.value.value
                      rulesArray = rulesValue.split("|")
                      rulesString = `:rules="[${rulesArray.map((v) => `rules.${v}`).join(", ")}]"`
                    }
                    fixes.push(
                      fixer.insertTextAfter(child.startTag.attributes.at(-1), indent + rulesString)
                    )
                    rulesArray.forEach((rule) => rulesToImport.add(rule))
                  }

                  fixes.push(
                    fixer.removeRange([
                      child.startTag.selfClosing ? child.startTag.range[1] : child.endTag.range[1],
                      node.endTag.range[1],
                    ])
                  )
                })

                if (rulesToImport.size) {
                  fixes.push(
                    fixer.insertTextBefore(
                      context.sourceCode.ast.body[0],
                      "import { " + [...rulesToImport].join(", ") + " } from '@/util/form'\n"
                    ),
                    fixer.insertTextAfterRange(
                      [vueObjectNode.range[0] + 1, vueObjectNode.range[0] + 1],
                      `
  setup() {
    return {
      rules: { ${[...rulesToImport].join(", ")} }
    }
  },`
                    )
                  )
                }

                return fixes
              },
            })
          },
          'VElement[rawName="ValidationObserver"]'(node) {
            if (observerNode) {
              throw new Error("multiple validation-observers")
            }
            observerNode = node
            formNode = node.children.find((child) => {
              return child.type === "VElement" && child.rawName === "form"
            })
          },
          'VElement[rawName="ValidationProvider"]'(node) {
            const children = node.children.filter((child) => {
              return child.type !== "VText" || child.value.trim()
            })
            const child = children[0]
            if (
              children.length !== 1 ||
              child.type !== "VElement" ||
              !(
                child.name.startsWith("v-") ||
                ["participant-select", "incident-select", "assignee-combobox"].includes(child.name)
              )
            ) {
              throw new Error(
                `validation-provider has unspported children at ${node.loc.start.line}:${node.loc.start.column}`
              )
            }
            const vid = node.startTag.attributes.find((attr) => {
              return (
                attr.type === "VAttribute" &&
                (attr.key.name === "vid" ||
                  (attr.directive &&
                    attr.key.name.name === "bind" &&
                    attr.key.argument?.name === "vid"))
              )
            })
            const name = node.startTag.attributes.find((attr) => {
              return (
                attr.type === "VAttribute" &&
                (attr.key.name === "name" ||
                  (attr.directive &&
                    attr.key.name.name === "bind" &&
                    attr.key.argument?.name === "name"))
              )
            })
            const rules = node.startTag.attributes.find((attr) => {
              return (
                attr.type === "VAttribute" &&
                (attr.key.name === "rules" ||
                  (attr.directive &&
                    attr.key.name.name === "bind" &&
                    attr.key.argument?.name === "rules"))
              )
            })
            const providerSlot = node.startTag.attributes.find((attr) => {
              return (
                attr.type === "VAttribute" &&
                attr.key.type === "VDirectiveKey" &&
                attr.key.name.name === "slot"
              )
            })
            const providerOtherAttrs = node.startTag.attributes
              .filter((attr) => {
                return (
                  attr !== vid &&
                  attr !== name &&
                  attr !== rules &&
                  attr !== providerSlot &&
                  attr.key?.name !== "immediate"
                )
              })
              .map((attr) => context.sourceCode.getText(attr))
            const childName = child.startTag.attributes.find((attr) => {
              return (
                attr.type === "VAttribute" &&
                (attr.key.name === "name" ||
                  (attr.directive &&
                    attr.key.name.name === "bind" &&
                    attr.key.argument?.name === "name"))
              )
            })
            const childRules = child.startTag.attributes.find((attr) => {
              return (
                attr.type === "VAttribute" &&
                (attr.key.name === "rules" ||
                  (attr.directive &&
                    attr.key.name.name === "bind" &&
                    attr.key.argument?.name === "rules"))
              )
            })

            if (providerOtherAttrs.length) {
              console.log("additional attributes", providerOtherAttrs)
              return context.report({
                node,
                message: "validation-provider has other attributes",
              })
            }

            if (providerSlot) {
              if (node.variables.length !== 1 || node.variables[0]?.id.name !== "errors") {
                return context.report({
                  node,
                  message: "validation-provider slot must only expose errors",
                })
              }
              if (
                node.variables[0].references.length !== 1 ||
                node.variables[0].references[0].id.parent.parent.type !== "VAttribute" ||
                node.variables[0].references[0].id.parent.parent.key.argument.name !==
                  "error-messages"
              ) {
                return context.report({
                  node: node.variables[0].references[0].id,
                  message: "validation-provider errors must only be used in error-messages",
                })
              }
            }

            if (childName) {
              return context.report({
                node: childName,
                message: "validation-provider child must not have a name",
              })
            }

            if (childRules) {
              return context.report({
                node: childRules,
                message: "validation-provider child should not have rules",
              })
            }

            validationProviderNodes.push({ node, child, rules, vid: vid || name })
          },
        },
        {
          'MemberExpression[object.type="MemberExpression"][object.property.name="$refs"][property.name="observer"]'(
            node
          ) {
            observerRefNodes.push(node)
          },
          'ImportDeclaration[source.value="vee-validate"]'(node) {
            vvImportNodes.push(node)
          },
          'ImportDeclaration[source.value="vee-validate/dist/rules"]'(node) {
            vvRuleImportNodes.push(node)
          },
          "ExportDefaultDeclaration > ObjectExpression"(node) {
            vueObjectNode = node
          },
          'ExportDefaultDeclaration > ObjectExpression > Property[key.name="setup"]'() {
            hasSetup = true
          },
          'ExportDefaultDeclaration > ObjectExpression > Property[key.name="methods"] > ObjectExpression > Property'(
            node
          ) {
            methodNodes.push(node)
          },
        }
      )
    },
  },
  "list-item-children": {
    meta: {
      fixable: "code",
    },
    create(context) {
      return context.parserServices.defineTemplateBodyVisitor({
        'VElement[name="v-list-item"]'(node) {
          if (
            node.startTag.attributes.some((attr) => attr.directive && attr.key.name.name === "slot")
          ) {
            return
          }

          const prepend = []
          const append = []
          let inContent = false
          let reachedContent = false
          let fixable = true
          for (const child of node.children) {
            if (child.type !== "VElement") {
              if (child.type === "VText" && !child.value.trim()) continue
              else {
                fixable = false
                break
              }
            } else if (
              ["v-list-item-title", "v-list-item-subtitle", "v-list-item-content"].includes(
                child.name
              )
            ) {
              if (reachedContent && !inContent) {
                fixable = false
                break
              }
              inContent = true
              reachedContent = true
            } else if (
              ["v-list-item-avatar", "v-list-item-icon", "v-list-item-action"].includes(child.name)
            ) {
              inContent = false
              if (child.startTag.attributes.length && child.name !== "v-list-item-avatar") {
                fixable = false
                break
              }
              if (reachedContent) {
                append.push(child)
              } else {
                prepend.push(child)
              }
            } else {
              fixable = false
              break
            }
          }

          if (prepend.length || append.length) {
            context.report({
              node,
              message: "move list item children into slots",
              *fix(fixer) {
                if (!fixable) return

                function stringifyChildren(children) {
                  return children
                    .flatMap((child) => {
                      if (child.name === "v-list-item-avatar") {
                        return context.sourceCode
                          .getText(child)
                          .replace(/<v-list-item-avatar(\s|>)/, "<v-avatar$1")
                          .replace("</v-list-item-avatar>", "</v-avatar>")
                      }
                      return child.children.map((v) => context.sourceCode.getText(v).trim())
                    })
                    .join("\n")
                }

                for (const child of prepend) {
                  yield fixer.remove(child)
                }
                for (const child of append) {
                  yield fixer.remove(child)
                }

                if (prepend.length) {
                  yield fixer.insertTextAfter(
                    node.startTag,
                    `<template #prepend>${stringifyChildren(prepend)}</template>`
                  )
                }
                if (append.length) {
                  yield fixer.insertTextBefore(
                    node.endTag,
                    `<template #append>${stringifyChildren(append)}</template>`
                  )
                }
              },
            })
          }
        },
      })
    },
  },
}
