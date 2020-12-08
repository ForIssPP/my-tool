# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class OneKmnMusicItem(Item):
    name = Field()
    author = Field()
    files = Field()
    file_urls = Field()
    lrc_contents = Field()
    keyword = Field()
    music_id = Field()


class OneKmnMusicUrlItem(Item):
    base_url = Field()
    urls = Field()
    keyword = Field()
    keyword_id = Field()
