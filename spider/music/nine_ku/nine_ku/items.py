# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class NineKuAuthorItem(Item):
    name = Field()
    url = Field()
    area = Field()
    birthday = Field()
    description = Field()
    songs = Field()
    song_ids = Field()


class NineKuMusicsItem(Item):
    music_id = Field()
    name = Field()
    url = Field()
    file_urls = Field()
    files = Field()
    author = Field()
