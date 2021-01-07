import re
from pathlib import Path
import logging

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class DownloadError(Exception):
    pass


class Download:
    download_dir = Path('assets')
    PNG = b'\xef\xbf\xbdPNG'
    parse_type_re = re.compile(r'(?:(?<=image/)|(?<=\.))(\w+)$')
    logger = logger
    download_name = None

    def __init__(self, url):
        self.url = url
        self.res = requests.get(url)
        if not self.download_dir.exists():
            self.download_dir.mkdir()
        if self.res.status_code != 200:
            raise DownloadError(f'下载错误, 返回码为: {self.res.status_code}')

    def parse_suffix(self):
        suffix = self.parse_type_re.search(self.url)
        if not suffix:
            suffix = self.parse_type_re.search(self.res.headers['Content-Type'])
        if suffix:
            suffix = suffix.group(0)
        else:
            suffix = bytes(self.res.text[:10], 'utf8')
            if not suffix.find(self.PNG):
                suffix = 'png'
        self.logger.info(f'下载类型: {suffix}')
        return suffix

    def save(self, key=None):
        if not key:
            key = re.search(r'(\w+)$', self.url).group(0)
        fn = self.download_dir / f'download-{key}.{self.parse_suffix()}'
        if fn.exists():
            self.logger.warning(f'文件已存在，此操作将会替换该文件')
        fn.write_bytes(self.res.content)
        self.download_name = fn
        return fn.name


if __name__ == '__main__':
    d_url = 'https://img.weichabao.com/blacklist/rep/2021/1/6/1270983367627'
    print(Download(d_url).save())
