const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema } = require('graphql');
const fs = require('fs');
const path = require('path');

const mockGql = fs.readFileSync(path.resolve(__dirname, 'mocks.gql'));

const schema = buildSchema(mockGql.toString());

const root = { student: () => [{ name: 'Bill', age: 18, test: 91.8 }] };

const app = express();

app.use(
  '/graphql',
  graphqlHTTP({
    schema: schema,
    rootValue: root,
    graphiql: true,
  })
);

app.listen(3001, () => console.log('http://localhost:3001/graphql'));
