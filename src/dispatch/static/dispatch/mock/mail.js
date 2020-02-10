const Faker = require("faker")
const Fs = require("fs")
let range = (start, end) => new Array(end - start).fill(start).map((el, i) => start + i)
const MailType = ["sent", "draft", "starred", "trashed"]
const MailTag = ["Promotion", "Work", "Personal", "Social"]
const users = JSON.parse(Fs.readFileSync("./static/data/user.json", "UTF-8"))
const Mails = range(0, 20).map(() => {
  let name = Faker.name.findName()
  return {
    uuid: Faker.random.uuid(),
    type: Faker.random.arrayElement(MailType),
    tag: Faker.random.arrayElement(MailTag),
    title: Faker.lorem.sentence(),
    created_at: Faker.date.recent(),
    content: Faker.lorem.paragraphs(5),
    fromId: Faker.random.arrayElement(users).uuid,
    attachments: Faker.random.boolean === true ? [Faker.image.nightlife()] : []
  }
})

module.exports = () => {
  return {
    data: Mails
  }
}
