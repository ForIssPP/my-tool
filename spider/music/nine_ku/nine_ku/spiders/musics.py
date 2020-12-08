import json

import scrapy
from scrapy.http import Request
from ..db import DB
from ..items import NineKuMusicsItem


class MusicsSpider(scrapy.Spider):
    name = 'musics'
    allowed_domains = ['*.9ku.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'nine_ku.pipelines.NineKuMusicDownloadPipeline': 1,
            'nine_ku.pipelines.NineKuMusicsPipeline': 300,
        },
        'FILES_STORE': './dist/downloads/',
        'FILES_EXPIRES': 90
    }

    def start_requests(self):
        db = DB()
        # sql = 'SELECT `id`, `name`, `author`, `url` FROM nineku_music.`musics` WHERE not path LIMIT 500'
        sql = "SELECT `id`, `name`, `author`, `url` FROM nineku_music.`musics` WHERE url LIKE '%.js'"
        db.cursor.execute(sql)
        musics = db.cursor.fetchall()
        if musics:
            for music_id, name, author, url in musics:
                yield Request(url, meta={'name': name, 'music_id': music_id, 'author': author}, dont_filter=True)

    def parse(self, response, **kwargs):
        items = NineKuMusicsItem()
        name = response.meta.get('name')
        author = response.meta.get('author')
        music_id = response.meta.get('music_id')
        context = json.loads(response.text[1:-1])
        url = context['wma']
        if url == '0':
            self.logger.warning(f'获取歌曲失败: {author}-{name}')
        else:
            items['author'] = author
            items['name'] = name
            items['music_id'] = music_id
            items['file_urls'] = [url]
            yield items
