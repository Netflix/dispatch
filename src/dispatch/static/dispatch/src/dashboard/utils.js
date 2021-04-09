import { at, countBy, isArray, mergeWith, forEach, map, find } from "lodash"

export default {
  createCountedSeriesData(items, itemKey, allKeys) {
    let series = []
    forEach(items, function (value) {
      let typeCounts = map(
        countBy(value, function (item) {
          return at(item, itemKey)
        }),
        function (value, key) {
          return { name: key, data: [value] }
        }
      )

      // fill in any missing gaps
      if (allKeys) {
        forEach(allKeys, function (type) {
          let found = find(typeCounts, { name: type })
          if (!found) {
            typeCounts.push({ name: type, data: [0] })
          }
        })
      }

      if (series.length) {
        series = forEach(series, function (value) {
          let currentType = find(typeCounts, { name: value.name })
          return mergeWith(value, currentType, function (objValue, srcValue) {
            if (isArray(objValue)) {
              return objValue.concat(srcValue)
            }
          })
        })
      } else {
        series = typeCounts
      }
    })

    // sort
    //series = sortBy(series, function(obj) {
    //  return types.indexOf(obj.name)
    //})
    return series
  },
  defaultColorTheme() {
    return [
      "#008FFB",
      "#00E396",
      "#FEB019",
      "#FF4560",
      "#775DD0",
      "#546E7A",
      "#4ECDC4",
      "#D4526E",
      "#2B908F",
      "#2E294E",
    ]
  },
}
