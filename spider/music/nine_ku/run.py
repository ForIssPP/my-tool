import os
from pathlib import Path
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

import pinyin
from nine_ku.db import DB
import json

from nine_ku.spiders.author import AuthorSpider
from nine_ku.spiders.musics import MusicsSpider


def write_love_author():
    db = DB()
    with Path('./initial-data.json').open('rb') as f:
        data = json.loads(f.read(), encoding='utf-8')
        love_author_data = data['love_author'].split(',')

    db.cursor.execute('''
    CREATE TABLE IF NOT EXISTS `author` (
        `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
        `initial_pinyin` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
        `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
        `area` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
        `birthday` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
        `description` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
        `status` int(11) NOT NULL DEFAULT '0',
        PRIMARY KEY (`name`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
    ''')
    db.cursor.execute('''
    CREATE TABLE IF NOT EXISTS `musics` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
        `author` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT '',
        `path` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
        `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
        `create_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        `update_date` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        PRIMARY KEY (`id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
    ''')

    sql = 'INSERT IGNORE INTO `author` (name, initial_pinyin, status) VALUES (%s, %s, %s)'
    db.cursor.executemany(sql, [(x, pinyin.get_initial(x[0]).lower(), 0) for x in love_author_data])
    # db.cursor.close()
    # db.connect.close()


@defer.inlineCallbacks
def crawl(runner):
    yield runner.crawl(AuthorSpider)
    yield runner.crawl(MusicsSpider)
    reactor.stop()
    # exit()
    # os.system('shutdown /p')


def main():
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    crawl(runner)

    reactor.run()


if __name__ == '__main__':
    write_love_author()
    main()
