import { Parser } from "json2csv"

const {
  transforms: { flatten },
} = require("json2csv")

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

const exportCSV = function (items, fileName) {
  const opts = { transforms: [flatten()] }
  const parser = new Parser(opts)
  const csv = parser.parse(items)
  const data = "data:text/csv;charset=utf-8," + encodeURIComponent(csv)
  const link = document.createElement("a")
  link.setAttribute("href", data)
  link.setAttribute("download", fileName)
  link.click()
}

export default {
  toggleFullScreen,
  exportCSV,
}
