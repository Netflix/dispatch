const Faker = require("faker")
const range = (start, end) => new Array(end - start).fill(start).map((el, i) => start + i)
const randomInt = max => Math.floor(Math.random() * max) + 1
const users = range(0, 20).map(() => {
  let name = Faker.name.firstName()
  let userName = Faker.internet.userName(name)
  return {
    uid: Faker.random.uuid(),
    name: name,
    email: Faker.internet.email(userName),
    username: userName,
    phone: Faker.phone.phoneNumber(),
    avatar: Faker.image.avatar(),
    address: {
      street: Faker.address.streetAddress(),
      suite: Faker.address.secondaryAddress(),
      city: Faker.address.city(),
      state: Faker.address.state(),
      country: Faker.address.country(),
      zipcode: Faker.address.zipCode(),
      geo: {
        lat: Faker.address.latitude(),
        lng: Faker.address.longitude()
      }
    }
  }
})

module.exports = () => {
  return {
    data: users
  }
}
