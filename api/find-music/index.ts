import fs from 'fs-extra';
import mysql from 'mysql';
import { join } from 'path';
import express from 'express';
import bodyParser from 'body-parser';
import childProcess from 'child_process';
import makePy from './make-pinyin';
import { find9KuMusic, find9KuMusicLRCText } from './find-music';

type Config = {
  web: {
    port: number;
  };
  db: mysql.ConnectionConfig;
};

const CONFIG: Config = JSON.parse(fs.readFileSync(join(__dirname, 'config.json')).toString());
const connection = mysql.createConnection(CONFIG.db);

connection.connect(err => {
  if (err) {
    switch (err.errno) {
      case 1045:
      case 1251:
        console.error('数据库用户名或密码错误');
        break;
      case 1049:
        console.log('请先创建数据库');
        break;
      default:
        console.error('未知错误: ', err);
    }

    connection.destroy();
  } else {
    createServer();
  }
});

function createServer() {
  const app = express();
  app.use(bodyParser.json({ limit: '1mb' }));
  app.use(bodyParser.urlencoded({ extended: true }));
  app.use('/static', express.static('./static/'));
  // API find
  app.post('/find/:music', async (req, res) => res.json(await find9KuMusic(req.params.music)));
  // API Select
  app.post('/select/:id', async (req, res) => {
    try {
      res.json({ lrcText: await find9KuMusicLRCText(req.params.id) });
    } catch (error) {
      res.json({ error: 1, message: '歌词加载失败' });
    }
  });
  // Website
  app.use('/', async (_req, res) => res.end(await fs.readFile(join(__dirname, './index.html'))));
  app.listen(CONFIG.web.port, () => console.log('服务器开始运行: http://localhost:' + CONFIG.web.port));
}
