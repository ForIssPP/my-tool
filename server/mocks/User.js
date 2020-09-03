const faker = require('faker');

class User {
  constructor(...friends) {
    if (friends) {
      this.friend.push(...friends);
    }
  }

  avatar = faker.image.avatar();
  name = faker.name.findName();
  address = faker.address.streetAddress();
  description = faker.lorem.sentences();
  friend = [];
}

module.exports = User;
