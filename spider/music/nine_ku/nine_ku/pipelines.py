import hashlib
import os
import re

from scrapy.utils.python import to_bytes
from scrapy.pipelines.files import FilesPipeline
import mimetypes
from .db import DB
import logging


class NineKuAuthorPipeline:
    def __init__(self):
        self.db = DB()

    def process_item(self, item, _spider):
        author = item['name']
        self.db.cursor.execute(f'''
            UPDATE `author` SET
                url='{item['url']}',
                area='{item['area']}',
                birthday='{item['birthday']}',
                description='{item['description']}',
                status=1
            WHERE name='{author}'
        ''')
        self.db.connect.commit()
        sql = 'INSERT INTO `musics` (name, author, url) VALUES (%s, %s, %s)'
        base_url = 'http://www.9ku.com/html/playjs/31/{}.js'
        data = []
        for i, song_id in enumerate(item['song_ids']):
            song = item['songs'][i]
            url = base_url.format(song_id)
            logging.info(f'song -> {song}')
            logging.info(f'url -> {url} \n')
            data.append((item['songs'][i], author, url.format(song_id)))
        self.db.cursor.executemany(sql, data)
        self.db.connect.commit()
        return item


class NineKuMusicDownloadPipeline(FilesPipeline):
    __r = re.compile(r'[<>?|\-:*/\0\f\t\n\r\v\\]')

    def file_path(self, request, response=None, info=None, *, item=None):
        media_ext = os.path.splitext(request.url)[1]
        name = self.__r.sub('', item.get('name', f'未知歌曲{hashlib.sha1(to_bytes(request.url)).hexdigest()}'))
        author = self.__r.sub('', item.get('author', '未知歌手'))
        media_guid = f"{author}/{name}"
        if not media_guid:
            media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()

        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.guess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)

        return f'{media_guid}{media_ext}'


class NineKuMusicsPipeline:
    def __init__(self):
        self.db = DB()

    def process_item(self, item, _spider):
        files = item['files']
        if files and files[0] and files[0]['path']:
            url = files[0]['url']
            path = files[0]['path']
            sql = f'''
                UPDATE nineku_music.`musics`
                SET url='{url}', path='{path}'
                WHERE id = {item['music_id']}
            '''
            logging.info(f'文件 {item["music_id"]} 下载成功 path -> {path} url -> {url}')
            self.db.cursor.execute(sql)
            self.db.connect.commit()
            return item
