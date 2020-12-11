import json
import random
import re
import time
from pathlib import Path
import requests
from utils.auto_submit import AutoSubmit, create_upload_boundary_img_files

ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'


class Default(AutoSubmit):
    domain = 'https://www.weichabao.com'
    upload_img_url = ''
    login_api = '/login'
    submit_url = '/marking/push'
    upload_img_file_keys = ['fileurl1']
    submit_img_key = 'file'
    login_params = ['phone', 'password']

    def created(self):
        self.headers['Accept'] = ACCEPT
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.headers['Method'] = 'POST'
        response = requests.get(self.domain, self.headers)
        self.cookies = dict(response.cookies)
        self.get_csrf_token(response)
        self.login_form['_token'] = self.csrf_token
        self.get_csrf_token(response)

    def parse_upload_img_src(self, upload_img_src):
        return [upload_img_src]

    def get_qiniu_token(self):
        result = requests.get('https://www.weichabao.com/marking/index', headers=self.headers, cookies=self.cookies)
        self.cookies = dict(result.cookies)
        self.get_csrf_token(result)
        token = re.search(r'name="qiniu_token" value="(.*?)"', result.text).group(1)
        form_token = re.search(r'name="form_token" value="(.*?)"', result.text).group(1)
        self.logger.info(f'{"Upload Img Token".center(20)}-> {token}')
        return form_token, token

    def get_submit_data(self, file_paths):
        upload_img_url = 'https://upload-z2.qiniup.com'
        form_token, token = self.get_qiniu_token()
        key = time.strftime('blacklist/rep/%Y/%m/%d', time.localtime()) + str(random.random())[2:]
        data = {'token': token, 'key': key, 'fname': Path(file_paths[0]).name}
        domain = self.domain
        self.update_content_type(None).domain = upload_img_url
        result = self.upload_boundary_img(file_paths, data=data)
        upload_result = json.loads(result.text)
        key = upload_result['key']
        data = self.submit_params
        data['_token'] = self.csrf_token
        data['form_token'] = form_token
        data['img'] = [key]
        self.domain = domain
        return data

if __name__ == '__main__':
    req = Default(
        '123456', '123456',  account='tb043043909', tags=[1, 2, 3],
        experience='刷单 给他返款了 隔了两天就是 淘宝上退款'
    )
    req.run([r'C:\Users\Lenovo\Desktop\666.png'])
