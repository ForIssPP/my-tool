import request from 'request';
import { createHash } from 'crypto';

interface QueryBody {
  q?: string;
  from?: string;
  to?: string;
}

interface APIResponse {
  ok: boolean;
  result: {
    trans_result: {
      src: string;
      dst: string;
    }[];
  };
}

const API_URL = 'http://api.fanyi.baidu.com/api/trans/vip/translate';

export default function (appid: string, key: string, body: QueryBody) {
  if (!appid || !key) {
    throw 'Not APPID or key';
  }

  const { q, from, to }: QueryBody = body;
  const salt = Date.now();

  if (!q || !from || !to) {
    const error: { [x: string]: string } = {};

    q ?? (error.q = 'Need a string value');
    from ?? (error.from = 'Need a string value');
    to ?? (error.to = 'Need a string value');

    return Promise.reject({
      ok: false,
      error,
      message: 'Con not find required data.'
    });
  } else {
    return new Promise<APIResponse>((resolve, reject) =>
      request.post(
        API_URL,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          formData: {
            q,
            from,
            to,
            appid,
            salt,
            sign: createHash('md5')
              .update(appid + q + salt + key)
              .digest('hex')
          }
        },
        (error, { body }) => {
          if (error) {
            return reject({ ok: false, error });
          } else {
            return resolve({ ok: true, result: JSON.parse(body) });
          }
        }
      )
    );
  }
}
