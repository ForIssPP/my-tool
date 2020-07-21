const app = require('express')();

app.get('/**', (res, rej) => {
  console.log(res.url);
  rej.end('');
});

app.post('/**', (res, rej) => {
  console.log(res.url);
  rej.end('');
});

app.listen(8081);
