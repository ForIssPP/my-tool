import fs from 'fs-extra';
import { join } from 'path';
import express from 'express';
import bodyParser from 'body-parser';

enum ApiType {
  baidu = 'baidu',
  google = 'google'
}

interface Conf {
  apiType: ApiType;
  appid: string;
  key: string;
  website: {
    port: number;
  };
}

interface TranslateTypes {
  label: string;
  value: string;
}

interface FetchTypesBody {
  q: string;
  from: string;
  to: string;
}

async function useConfTranslateAPI(body: FetchTypesBody) {
  switch (CONF.apiType) {
    case ApiType.baidu:
      return await (await import('./baidu')).default(CONF.appid, CONF.key, body);
    case ApiType.google:
      throw 'Can not has google translate api.';
    default:
      throw 'Can not find translate api.';
  }
}

async function fetchTypes(type: string) {
  if (typesMap.has(type)) {
    return typesMap.get(type);
  } else {
    const value = (
      await useConfTranslateAPI({
        q: DEFALUT_EN_TYPES.map(({ label }) => label).join('\n'),
        from: 'en',
        to: type
      })
    ).result.trans_result.map(({ dst, src }) => ({
      label: dst,
      value: DEFALUT_EN_TYPES[DEFALUT_EN_TYPES.findIndex(({ label }) => label === src)].value
    }));

    typesMap.set(type, value);
    return value;
  }
}

const DEFALUT_TYPES = [
  { label: '自动', value: 'auto' },
  { label: '中文', value: 'zh' },
  { label: '英文', value: 'en' }
];
const DEFALUT_EN_TYPES = [
  { label: 'Auto', value: 'auto' },
  { label: 'Chinese', value: 'zh' },
  { label: 'English', value: 'en' }
];
const CONF: Conf = JSON.parse(fs.readFileSync(join(__dirname, './config.json')).toString());
const typesMap = new Map<string, TranslateTypes[]>([
  ['zh', DEFALUT_TYPES],
  ['en', DEFALUT_EN_TYPES]
]);
const app = express();

app.use(bodyParser.json({ limit: '1mb' }));
app.use(bodyParser.urlencoded({ extended: true }));
app.use('/static', express.static('./static/'));
app.post('/api/fetch/types', async ({ body }, res) => res.json(typesMap.get(body.lang ?? 'zh') ?? (await fetchTypes(body.lang))));
app.use('/api/post/translate', async (req, res) => res.json(await useConfTranslateAPI(req.body)));
app.use('*', async (_req, res) => res.end(await fs.readFile(join(__dirname, './index.html'))));
app.listen(CONF.website.port, console.log.bind(null, `Website server is run http://localhost:${CONF.website.port}`));
