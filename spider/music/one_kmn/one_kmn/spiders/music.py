import re
import scrapy
from scrapy.http import Request
from ..items import OneKmnMusicItem
from ..utils.mysql_cnn import CreateMysqlConnector


class MusicSpider(scrapy.Spider):
    name = 'music'
    allowed_domains = ['m.1kmn.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'one_kmn.pipelines.OneKmnMusicsPipeline': 300,
        },
        'FILES_STORE': './dist/downloads/',
        'FILES_EXPIRES': 90
    }

    def start_requests(self):
        db = CreateMysqlConnector()
        db.cursor.execute('SELECT id, url, keyword FROM music_urls WHERE has_download = 0;')
        result = db.cursor.fetchall()
        for music_id, url, keyword in result:
            yield Request(url, dont_filter=True, meta={'music_id': music_id, 'keyword': keyword})

    def parse(self, response, **kwargs):
        items = OneKmnMusicItem()
        keyword = response.meta.get('keyword')
        lrc_content = str(response.css('pre.aplayer-lrc-content::text').extract_first())
        items['lrc_contents'] = lrc_content
        items['file_urls'] = [response.css('div.plr10 a::attr(href)').extract_first()]
        items['keyword'] = keyword
        items['music_id'] = response.meta.get('music_id')
        search_result = re.search(r'\[ar:(.+?)\].*\[ti:(.+?)\]', lrc_content)
        if search_result:
            items['author'] = search_result.group(1)
            items['name'] = search_result.group(2)
        else:
            items['author'] = keyword
            items['name'] = keyword

        yield items
