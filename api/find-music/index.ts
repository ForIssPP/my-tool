import fs from 'fs-extra';
import mysql, { MysqlError } from 'mysql';
import { join } from 'path';
import express from 'express';
import bodyParser from 'body-parser';
import { find9KuMusic, find9KuMusicLRCText, Song } from './find-music';
import axios from 'axios';
// import makePy from './make-pinyin';

type Config = {
  web: {
    port: number;
  };
  db: mysql.ConnectionConfig;
};

if (!fs.existsSync(join(__dirname, 'config.json'))) {
  console.log('请先配置Config.json');
  console.log(`example:
  {
    "db": {
      "host": "localhost",
      "user": "root",
      "password": "123456",
      "database": "find_music"
    },
    "web": {
      "port": 8003
    }
  }
  `);
  throw Error('config.json is not find!');
}

const CONFIG: Config = JSON.parse(fs.readFileSync(join(__dirname, 'config.json')).toString());
const connection = mysql.createConnection(CONFIG.db);
const sqlQuery = <T = { message: string }>(sql: string, ...args: any[]) =>
  new Promise<T>((resolve, reject) =>
    connection.query(sql, ...args, (error: MysqlError, result: any) => (error ? reject(error) : resolve(result)))
  );
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
    sqlQuery(fs.readFileSync('./db.sql').toString()).then(createServer).catch(console.error);
  }
});

function createServer() {
  const app = express();
  app.use(bodyParser.json({ limit: '1mb' }));
  app.use(bodyParser.urlencoded({ extended: true }));
  app.use('/static', express.static('./static/'));
  // API find
  app.post('/find/:music', async (req, res) => {
    const music = req.params.music;
    try {
      const sqlRes = await sqlQuery<Song[]>(`SELECT * FROM musics WHERE name='${music}' or author='${music}'`);
      if (sqlRes.length) {
        res.json(sqlRes);
      } else {
        const songs = await find9KuMusic(music);
        if (songs.length) {
          res.json(songs);
          try {
            const sqlRes = await sqlQuery(
              'INSERT INTO musics (id, name, author, authorPicture, album, albumPicture, src) VALUES ?',
              songs.map(({ id, name, author, authorPicture, album, albumPicture, src }) => [
                parseInt(id),
                name,
                author,
                authorPicture,
                album,
                albumPicture,
                src
              ])
            );
            console.log(sqlRes.message);
          } catch (error) {
            console.error(error);
          }
        } else {
          res.json({ error: 1, music });
        }
      }
    } catch (error) {
      res.json({ error: 1, music, errorContent: error });
    }
  });
  // API Select
  app.post('/select/:id', async (req, res) => {
    try {
      res.json({ lrcText: await find9KuMusicLRCText(req.params.id) });
    } catch (error) {
      res.json({ error: 1, message: '歌词加载失败' });
    }
  });
  app.use('/download/:id', async (req, res) => {
    try {
      const { id } = req.params;
      const songs = await sqlQuery<Song[]>(`SELECT * FROM musics WHERE id=${id}`);
      const song = await axios({ url: songs[0].src, responseType: 'stream' });
      song.data.pipe(res);
    } catch (error) {
      res.status(400).json({ error: 1, errorContent: error });
    }
  });
  // Website
  app.use('/', async (_req, res) => res.end(await fs.readFile(join(__dirname, './index.html'))));
  app.listen(CONFIG.web.port, () => console.log('服务器开始运行: http://localhost:' + CONFIG.web.port));
}
