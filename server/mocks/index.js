const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema } = require('graphql');
const fs = require('fs');
const path = require('path');
const User = require('./User');

const app = express();
const PORT = 3001;
const DEFAULT_PATH = '/graphql';
const mockGql = fs.readFileSync(path.resolve(__dirname, 'mocks.gql'));
const schema = buildSchema(mockGql.toString());

const mockData = {
  users: ({ id }) => (
    console.log('query id ->', id),
    [
      new User(
        new User(new User(), new User()),
        new User(new User()),
        new User()
      ),
    ]
  ),
};

app.use(
  DEFAULT_PATH,
  graphqlHTTP({
    schema: schema,
    rootValue: mockData,
    graphiql: true,
  })
);

app.listen(PORT, () => console.log(`http://localhost:${PORT}${DEFAULT_PATH}`));
