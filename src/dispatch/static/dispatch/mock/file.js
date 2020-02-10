const fs = require("fs")
const path = require("path")
const faker = require("faker")
const mime = require("mime-types")
const walkSync = (dir, filelist = [], exclude = []) => {
  let files = fs.readdirSync(dir) || []
  filelist = filelist || []
  files.forEach(name => {
    let filePath = path.join(dir, name)
    let file = {}
    let fileStat = fs.statSync(filePath)
    let fullPath = path.resolve(filePath)
    let parse = path.parse(filePath)
    let fileType = mime.lookup(filePath)
    if (fileStat.isDirectory()) {
      filelist = walkSync(filePath, filelist)
    } else {
      file = {
        uuid: faker.random.uuid(),
        fileName: name,
        fileType: fileType,
        path: filePath,
        fullPath: fullPath,
        ext: parse.ext,
        dir: parse.dir,
        ctime: fileStat.ctime,
        size: fileStat.size
      }
      filelist.push(file)
    }
  })
  return filelist
}
const files = walkSync("./static", [], [])

module.exports = () => {
  return {
    data: files
  }
}
