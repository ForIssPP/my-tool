import express from 'express';
import bodyParser from 'body-parser';
import request from 'axios';

const app = express();
const URL = 'https://api.rebrandly.com/v1/links';
const KEY = '';

interface FetchShortURLPrams {
  url: string;
}

interface Response {
  id: string;
  title: string;
  slashtag: string;
  destination: string;
  createdAt: string;
  updatedAt: string;
  status: string;
  tags: string[] | number[];
  clicks: number;
  isPublic: false;
  shortUrl: string;
  domainId: string;
  domainName: string;
  domain: {
    id: string;
    ref: string;
    fullName: string;
    sharing: {
      protocol: {
        allowed: string[];
        default: string;
      };
    };
    active: true;
  };
  https: true;
  favourite: false;
  creator: {
    id: string;
    fullName: string;
    avatarUrl: string;
  };
  integrated: false;
}

async function fetchShortURL({ url }: FetchShortURLPrams) {
  if (!KEY) return { error: "Required String parameter 'key' is not present" };
  if (!url) return { error: "Required String parameter 'url' is not present" };

  try {
    const result = await request({
      url: URL,
      method: 'POST',
      data: {
        domain: { fullName: 'rebrand.ly' },
        destination: url
      },
      headers: {
        'Content-Type': 'application/json',
        apikey: KEY
      }
    });
    const data: Response = result.data;

    return { shortUrl: 'https://' + data.shortUrl };
  } catch (error) {
    return { error };
  }
}

app.use(bodyParser.json({ limit: '1mb' }));
app.use(bodyParser.urlencoded({ extended: true }));
app.use('/static', express.static('./static/'));
app.post('*', async (req, res) => res.json(await fetchShortURL(req.body)));
app.get('*', async (req, res) => res.json(await fetchShortURL(req.query as any)));
app.listen(8080, '0.0.0.0');
