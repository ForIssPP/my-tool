import scrapy
from scrapy.http import Request

from ..items import OneKmnMusicUrlItem
from ..utils.mysql_cnn import CreateMysqlConnector


class MusicUrlSpider(scrapy.Spider):
    name = 'music-url'
    allowed_domains = ['m.1kmn.com']
    # 歌曲、作者
    keywords = ['烟花易冷']
    start_url = 'http://m.1kmn.com/'
    query_keyword = '?ac='

    custom_settings = {
        'ITEM_PIPELINES': {
            'one_kmn.pipelines.OneKmnUrlPipeline': 300,
        }
    }

    def start_requests(self):
        db = CreateMysqlConnector()
        db.cursor.execute('SELECT DISTINCT id, keyword FROM keywords WHERE has_find = 0;')
        result = db.cursor.fetchall()
        for keyword_id, keyword in result:
            url = self.start_url + self.query_keyword + keyword
            yield Request(url, dont_filter=True, meta={'keyword_id': keyword_id, 'keyword': keyword})

    def parse(self, response, **kwargs):
        items = OneKmnMusicUrlItem()
        items['keyword'] = response.meta.get('keyword')
        items['keyword_id'] = response.meta.get('keyword_id')
        items['base_url'] = self.start_url
        items['urls'] = response.css('#wlsong li a.gname::attr(href)').extract()
        yield items
