import scrapy
from scrapy.http import Request
import re

from ..db import DB
from ..items import NineKuAuthorItem


class AuthorSpider(scrapy.Spider):
    name = 'author'
    allowed_domains = ['http://www.9ku.com/']
    start_url = 'http://www.9ku.com'
    _name_list = {}
    custom_settings = {
        'ITEM_PIPELINES': {
            'nine_ku.pipelines.NineKuAuthorPipeline': 300,
        },
    }

    def start_requests(self):
        db = DB()
        db.cursor.execute(
            'SELECT `name`, `url`, `initial_pinyin` FROM `author` WHERE status = 0 ORDER BY initial_pinyin'
        )
        authors = db.cursor.fetchall()
        for name, url, initial_pinyin in authors:
            if not url:
                url = f'http://baidu.9ku.com/song/?key={name}'
                yield Request(url, dont_filter=True, meta={'name': name}, callback=self.parse_author_page)
            else:
                yield Request(url, dont_filter=True, callback=self.parse, meta={'name': name})

    def crawl_url(self, name, response):
        url = response.css('a.singerName::attr(href)').extract_first()
        self.logger.info(f'查询歌手 -> {name} 成功 url: {url}')
        return Request(url, dont_filter=True, callback=self.parse, meta={'name': name})

    def parse_author_page(self, response):
        name = response.meta.get('name')
        first_link_name = response.css('a.singerName::text').extract_first()
        if name in first_link_name:
            yield self.crawl_url(name, response)
        else:
            names = response.css('a.singerName::text').extract()
            for link_name in names:
                if name in link_name:
                    yield self.crawl_url(name, response)
                    break
            # self.logger.info(f'查询歌手 -> {name} 失败')

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
        # file_urls = []
        # while ids:
        #     song_id = ids.pop(0)
        #     url = f'http://www.9ku.com/html/playjs/31/{song_id}.js'
        #     file_url = self.parse_song_page(url)
        #     self.logger.info(f'mp3 -> {file_url}')
        #     file_urls.append(file_url)
        yield items
    # def parse_song_page(self, url):
    #     response = requests.get(url)
    #     context = json.loads(response.text[1:-1])
    #     url = context['wma']
    #     # mp3_pic = context['zjpic']
    #     return url
