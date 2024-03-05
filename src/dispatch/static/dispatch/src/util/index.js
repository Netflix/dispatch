import { Parser } from "@json2csv/plainjs"
import { flatten } from "@json2csv/transforms"

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
  const json2csvParser = new Parser({ transforms: [flatten()] })
  const csv = json2csvParser.parse(items)
  const data = "data:text/csv;charset=utf-8," + encodeURIComponent(csv)
  const link = document.createElement("a")
  link.setAttribute("href", data)
  link.setAttribute("download", fileName)
  link.click()
}

// usage: fieldOrder is a list of field names in the order you want them to appear in the CSV
const exportCSVOrdered = function (items, fileName, fieldOrder) {
  const json2csvParser = new Parser({ transforms: [flatten()], fields: fieldOrder })
  const csv = json2csvParser.parse(items)
  const data = "data:text/csv;charset=utf-8," + encodeURIComponent(csv)
  const link = document.createElement("a")
  link.setAttribute("href", data)
  link.setAttribute("download", fileName)
  link.click()
}

export default {
  toggleFullScreen,
  exportCSV,
  exportCSVOrdered,
}
