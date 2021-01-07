import scrapy
from scrapy.http import Request
import re

from ..db import DB
from ..items import NineKuAuthorItem


class AuthorSpider(scrapy.Spider):
    name = 'author'
    allowed_domains = ['9ku.com']
    start_url = 'http://www.9ku.com'
    _name_list = {}
    custom_settings = {
        'ITEM_PIPELINES': {
            'nine_ku.pipelines.NineKuAuthorPipeline': 300,
        },
    }

    def start_requests(self):
        d = DB()
        d.cursor.execute(
            'SELECT `name`, `url`, `initial_pinyin` FROM `author` WHERE status = 0 ORDER BY initial_pinyin'
        )
        authors = d.cursor.fetchall()
        for name, url, initial_pinyin in authors:
            if not url:
                url = f'http://baidu.9ku.com/song/?key={name}'
                meta = {'name': name, 'initial_pinyin': initial_pinyin}
                yield Request(url, dont_filter=True, meta=meta, callback=self.parse_author_page)
            else:
                yield Request(url, dont_filter=True, callback=self.parse, meta={'name': name})

    def parse_all_author_page(self, response):
        name = response.meta.get('name')
        links = response.css('.filter_list .t-t')
        for link in links:
            if link.css('::text').extract_first() == name:
                url = self.start_url + link.css('::attr(href)').extract_first()
                self.logger.info(f'歌手: {name} 的访问连接为: {url}')
                return Request(url, dont_filter=True, callback=self.parse, meta={'name': name})

    def parse_author_page(self, response):
        name = response.meta.get('name')
        if response.status == 302 or response.status == 301:
            self.logger.warning(f'连接已重置，尝试使用首字母查询模式')
            initial_pinyin = response.meta.get('initial_pinyin')
            url = f'http://www.9ku.com/geshou/all-{initial_pinyin}-all.htm'
            return Request(url, dont_filter=True, callback=self.parse_all_author_page, meta={'name': name})
        else:
            links = response.css('a.singerName')
            for link in links:
                if name in link.css('::text').extract_first():
                    url = link.css('::attr(href)').extract_first()
                    self.logger.info(f'查询歌手 -> {name} 成功 url: {url}')
                    return Request(url, dont_filter=True, callback=self.parse, meta={'name': name})
            self.logger.info(f'查询歌手 -> {name} 失败')

    def parse(self, response, **kwargs):
        self.logger.info('------ 开始写入数据 ------')
        items = NineKuAuthorItem()
        link_elms = response.css('.songName .songNameA')
        # name = response.css('h1::text').extract_first()
        name = response.meta.get('name')
        description = response.css('.jianjieAll p::text').extract_first()
        hot = response.css('.redu em::text').extract_first()
        area, birthday = response.css('.i-t p:nth-child(1)::text').extract()
        songs = link_elms.css('::text').extract()
        links = link_elms.css('::attr(href)').extract()
        song_ids = [re.search('/play/([0-9]+).htm', link).group(1) for link in links]

        items['url'] = response.url
        items['name'] = name
        items['area'] = area[:-2]
        items['birthday'] = birthday
        items['description'] = description
        items['songs'] = songs
        items['song_ids'] = song_ids

        self.logger.info(f'name: {name}')
        self.logger.info(f'hot: {hot}')
        self.logger.info(f'area: {area[:-2]}')
        self.logger.info(f'birthday: {birthday}')
        self.logger.info(f'description: {description}')
        self.logger.info(f'songs: {songs}')
        self.logger.info(f'song_ids: {song_ids}')
        yield items
