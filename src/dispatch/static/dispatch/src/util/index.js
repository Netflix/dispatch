import { flatMap, isPlainObject } from "lodash"

const toggleFullScreen = () => {
  let doc = window.document
  let docEl = doc.documentElement

  let requestFullScreen =
    docEl.requestFullscreen ||
    docEl.mozRequestFullScreen ||
    docEl.webkitRequestFullScreen ||
    docEl.msRequestFullscreen
  let cancelFullScreen =
    doc.exitFullscreen ||
    doc.mozCancelFullScreen ||
    doc.webkitExitFullscreen ||
    doc.msExitFullscreen

  if (
    !doc.fullscreenElement &&
    !doc.mozFullScreenElement &&
    !doc.webkitFullscreenElement &&
    !doc.msFullscreenElement
  ) {
    requestFullScreen.call(docEl)
  } else {
    cancelFullScreen.call(doc)
  }
}

const mapValuesFlat = (obj) => {
  return flatMap(obj, (v) => {
    if (isPlainObject(v)) {
      return mapValuesFlat(v)
    }
    return v
  })
}

const exportCSV = function (items, fileName) {
  let csvContent = "data:text/csv;charset=utf-8,"
  csvContent += [
    Object.keys(items[0]).join(","),
    ...items.map((item) => {
      if (typeof item === "object") {
        return Object.values(item)
          .map((value) => {
            if (value === null) {
              return ""
            }
            if (typeof value === "object") {
              return mapValuesFlat(value).join("|")
            }
            return value
          })
          .join(",")
      }
      return ""
    }),
  ]
    .join("\n")
    .replace(/(^\[)|(\]$)/gm, "")

  const data = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", data)
  link.setAttribute("download", fileName)
  link.click()
}

export default {
  toggleFullScreen,
  exportCSV,
}
