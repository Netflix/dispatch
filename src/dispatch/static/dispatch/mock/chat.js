const Faker = require("faker")
const Fs = require("fs")
const range = (start, end) => new Array(end - start).fill(start).map((el, i) => start + i)
const randomInt = max => Math.floor(Math.random() * max) + 1
const randomArray = (arr, n) => {
  let result = new Array(n)
  let len = arr.length
  let taken = new Array(len)

  if (n > len) {
    throw new RangeError("getRandom: more elements taken than available")
  }

  while (n--) {
    let x = Math.floor(Math.random() * len)
    result[n] = arr[x in taken ? taken[x] : x]
    taken[x] = --len in taken ? taken[len] : len
  }
  return result
}

const users = JSON.parse(Fs.readFileSync("./static/data/user.json", "UTF-8"))
const uids = []
users.forEach(item => {
  uids.push(item.uuid)
})
const chatGroup = range(0, 10).map(() => {
  return {
    uuid: Faker.random.uuid(),
    title: Faker.lorem.word(),
    users: randomArray(uids, Faker.random.number({ min: 1, max: 3 })),
    created_by: Faker.random.arrayElement(uids),
    created_at: Faker.date.recent()
  }
})

module.exports = () => {
  return {
    data: chatGroup
  }
}
