from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from music.one_kmn.one_kmn.spiders.music_url import MusicUrlSpider
from music.one_kmn.one_kmn.spiders.music import MusicSpider
from music.one_kmn.one_kmn.utils.mysql_cnn import CreateMysqlConnector


@defer.inlineCallbacks
def crawl(runner):
    yield runner.crawl(MusicUrlSpider)
    yield runner.crawl(MusicSpider)
    reactor.stop()

def main(keywords):
    db = CreateMysqlConnector()
    db.create_table('keywords', 'id INT AUTO_INCREMENT PRIMARY KEY', 'keyword VARCHAR(255)', 'has_find INT(1)')
    sql = 'INSERT INTO keywords (keyword, has_find) values (%s, %s)'
    db.cursor.executemany(sql, [(x, 0) for x in keywords])
    db.connect.commit()

    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    crawl(runner)

    reactor.run()


if __name__ == '__main__':
    main(input('keywords(多个使用英文,分割): ').split(','))
