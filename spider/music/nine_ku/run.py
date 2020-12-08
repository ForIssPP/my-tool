import os
from pathlib import Path
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

import pinyin
from music.nine_ku.nine_ku.db import DB
import json

from music.nine_ku.nine_ku.spiders.author import AuthorSpider
from music.nine_ku.nine_ku.spiders.musics import MusicsSpider


def write_love_author():
    db = DB()
    with Path('./initial-data.json').open('rb') as f:
        data = json.loads(f.read(), encoding='utf-8')
        love_author_data = data['love_author'].split(',')

    sql = 'INSERT IGNORE INTO `author` (name, initial_pinyin, status) VALUES (%s, %s, %s)'

    db.cursor.executemany(sql, [(x, pinyin.get_initial(x[0]).lower(), 0) for x in love_author_data])


@defer.inlineCallbacks
def crawl(runner):
    yield runner.crawl(MusicsSpider)
    reactor.stop()
    os.system('shutdown /p')


def main():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    crawl(runner)

    reactor.run()


if __name__ == '__main__':
    write_love_author()
    main()
