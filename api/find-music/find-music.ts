import request, { AxiosResponse } from 'axios';

interface DetailSongsBy9KuMusic {
  id: string;
  id2: string;
  mname: string;
  gsid: string;
  singer: string;
  wma: string;
  m4a: string;
  zjid: string;
  zjname: string;
  zjpic: string;
  gspic: string;
  status: '0' | '1';
}

export interface Song {
  id: string;
  src: string;
  name: string;
  author: string;
  authorPicture: string;
  album: string;
  albumPicture: string;
}

const findHrefRE = /(?<=<a.+?href=['"].+?play\/)(\d+)(?=.htm['"].*?<\/a>)/g;

export async function find9KuMusic(kw: string): Promise<Song[]> {
  const url = 'https://baidu.9ku.com/suggestions/?kw=' + encodeURI(kw);
  const res = await request.get<string>(url);
  const songsLink = res.data.match(findHrefRE)?.map(str => `https://www.9ku.com/html/playjs/31/${str}.js`);
  if (songsLink) {
    const fetchSongsResponse = await request.all<AxiosResponse<string>>(songsLink.map(link => request.get(link)));
    const songs: DetailSongsBy9KuMusic[] = fetchSongsResponse.map(str => JSON.parse(str.data.slice(1, str.data.length - 1)));
    return songs.map(song => ({
      id: song.id,
      src: song.wma,
      name: song.mname,
      author: song.singer,
      authorPicture: song.gspic,
      album: song.zjname,
      albumPicture: song.zjpic
    }));
  }
  return [];
}

const findLRCTextRE = /(?<=<textarea.*?id="lrc_content".*?>)([\s\S]*?)(?=<\/textarea>)/g;

export async function find9KuMusicLRCText(id: number | string) {
  const url = `https://www.9ku.com/play/${id}.htm`;
  const res = await request.get<string>(url);
  const text = res.data.match(findLRCTextRE)?.map(str => str.replace(/[\r\n]/g, ''));
  if (text) {
    return text[0].replace(/(?<=[\d\d:\d\d]*)https?:..www.9ku.com欢迎您/, '');
  }
  return '';
}
