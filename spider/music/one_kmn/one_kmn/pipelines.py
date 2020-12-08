# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from .utils.mysql_cnn import CreateMysqlConnector


class OneKmnMusicsPipeline:
    def __init__(self):
        self.db = CreateMysqlConnector()
        self.db.cursor.execute('SHOW TABLES')
        self.db.create_table('musics', *[
            'id INT AUTO_INCREMENT PRIMARY KEY',
            'keyword VARCHAR(255)',
            'name VARCHAR(255)',
            'author VARCHAR(255)',
            'path VARCHAR(255)',
            'file_url VARCHAR(255)',
            'lrc_contents TEXT',
        ])

    def process_item(self, item, _spider):
        sql = '''
        INSERT INTO musics (
            keyword, 
            name,
            author,
            file,
            file_urls,
            lrc_contents
        ) VALUES ("{}", "{}", "{}", "{}", "{}", "{}")
        '''.format(
            item['keyword'],
            item['name'],
            item['author'],
            item['files'][0]['path'],
            item['files'][0]['url'],
            item['lrc_contents'],
        )
        self.db.cursor.execute(sql)
        self.db.connect.commit()

        music_id = item['music_id']
        self.db.cursor.execute(f'UPDATE music_urls SET has_download = 1 WHERE id = {music_id}')
        return item

    def close_spider(self, _spider):
        self.db.cursor.close()
        self.db.connect.close()


class OneKmnUrlPipeline:
    def __init__(self):
        self.db = CreateMysqlConnector()
        self.db.cursor.execute('SHOW TABLES')
        self.db.create_table(
            'music_urls',
            'id INT AUTO_INCREMENT PRIMARY KEY',
            'keyword VARCHAR(255)',
            'url VARCHAR(255)',
            'has_download INT(1)'
        )

    def process_item(self, item, _spider):
        urls = list(set(item['urls']))
        sql = 'INSERT INTO music_urls (keyword, url, has_download) VALUES (%s, %s, %s)'
        self.db.cursor.executemany(sql, [(item['keyword'], item['base_url'] + x, 0) for x in urls])
        self.db.connect.commit()
        keyword_id = item['keyword_id']
        self.db.cursor.execute(f'UPDATE keywords SET has_find = 1 WHERE id = {keyword_id}')
        return item

    def close_spider(self, _spider):
        self.db.cursor.close()
        self.db.connect.close()
