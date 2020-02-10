const Faker = require("faker")
const Fs = require("fs")
const range = (start, end) => new Array(end - start).fill(start).map((el, i) => start + i)
const randomInt = max => Math.floor(Math.random() * max) + 1
// chats
const chats = JSON.parse(Fs.readFileSync("./static/data/chat.json", "UTF-8"))
const chatIds = []
const messages = []
chats.forEach(item => {
  item.users.forEach(userId => {
    range(0, randomInt(4)).forEach(() => {
      messages.push({
        uuid: Faker.random.uuid(),
        chatId: item.uuid,
        text: Faker.lorem.sentence(),
        userId: userId,
        created_at: Faker.date.recent()
      })
    })
  })
})
// users

module.exports = () => {
  return {
    data: messages
  }
}
