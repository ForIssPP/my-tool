import fs from 'fs-extra';
import { join } from 'path';
import express from 'express';
import bodyParser from 'body-parser';
import request from 'axios';
import { program } from 'commander';

interface Conf {
  apiUrl: string;
  key?: string;
  format: 'json' | 'jsonp';
  defaultExpireDate: string;
  website: {
    port: number;
    url: string;
  };
}

interface FetchShortURLPrams {
  url: string;
  format?: Conf['format'];
  expireDate?: string;
  callback?: string;
  key: string;
}

async function fetchShortURL({
  url,
  key,
  callback,
  format = CONF.format,
  expireDate = CONF.defaultExpireDate
}: FetchShortURLPrams) {
  if (!key) return { error: "Required String parameter 'key' is not present" };
  if (!url) return { error: "Required String parameter 'url' is not present" };
  if (format === 'jsonp' && !callback) return { error: "Required String parameter 'callback' is not present" };

  try {
    const { data } = await request.get(
      `${CONF.apiUrl}?url=${url}&format=${format}&key=${key}&expireDate=${expireDate}&callbak=${callback}`
    );

    return data;
  } catch (error) {
    console.error(error);
    return { error };
  }
}

const CONF_PATH = join(__dirname, './config.json');
const configExists = fs.existsSync(CONF_PATH);

if (!configExists) {
  fs.writeFileSync(
    CONF_PATH,
    JSON.stringify({
      apiUrl: 'http://mrw.so/api.htm',
      format: 'json',
      defaultExpireDate: '2099-01-01',
      website: {
        port: 8080,
        url: '/api/shorturl'
      }
    })
  );
}

const CONF: Conf = JSON.parse(fs.readFileSync(CONF_PATH).toString());

if (configExists) {
  program.option('-k, --key [key]', 'key参数', CONF.key);
} else {
  program.option('-k, --key <key>', 'key参数');
}

program
  .option('-url, --url [url]', 'URL参数')
  .option('-f, --format [format]', 'format参数', CONF.format)
  .option('-e, --expire-date [date]', 'expireDate参数', CONF.defaultExpireDate)
  .option('-cb, --callback [callback]', 'callback参数')
  .option('-s, --start-server', '开启 server 服务器', true)
  .version('1.0.0');

program.parse(process.argv);
CONF.key = program.key;
fs.writeFileSync(CONF_PATH, JSON.stringify(CONF));

if (program.startServer) {
  const app = express();
  app.use(bodyParser.json({ limit: '1mb' }));
  app.use(bodyParser.urlencoded({ extended: true }));
  app.use('/static', express.static('./static/'));
  app.post(CONF.website.url, async (req, res) => res.json(await fetchShortURL(req.body)));
  app.get(CONF.website.url, async (req, res) => res.json(await fetchShortURL(req.query as any)));
  app.listen(CONF.website.port, '0.0.0.0', console.log.bind(null, `Website server is run http://localhost:${CONF.website.port}`));
} else {
  const log = async () =>
    console.log(
      '编译的短链接 ->',
      (
        await fetchShortURL({
          key: program.key,
          url: program.url,
          format: program.format,
          expireDate: program.date,
          callback: program.callback
        })
      ).url
    );

  log();
}
