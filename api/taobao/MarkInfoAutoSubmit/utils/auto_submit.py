import json
import logging
import re
from datetime import datetime
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import requests
from faker import Faker

logger = logging.getLogger('AutoSubmit')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class AutoModules:
    LOG_SPACE_COUNT = 30
    domain = None
    faker = Faker()

    def __init__(self):
        self.headers = {
            "User-Agent": self.faker.user_agent()
        }
        self.cookies = {}
        self.logger = logger

    def update_content_type(self, content_type):
        self.headers['Content-Type'] = content_type
        return self

    def fetch(self, url, **kw):
        self.logger.debug(f'----------------------------------')
        self.logger.debug(f'{"Fetch url".center(self.LOG_SPACE_COUNT)}-> {url}')
        if 'files' not in kw:
            self.logger.debug(f'{"Fetch keywords".center(self.LOG_SPACE_COUNT)}-> {kw}')
        self.logger.debug(f'{"Fetch cookies".center(self.LOG_SPACE_COUNT)}-> {self.cookies}')
        self.logger.debug(f'{"Fetch Headers".center(self.LOG_SPACE_COUNT)}-> {self.headers}')
        result = requests.post(self.domain + url, cookies=self.cookies, headers=self.headers, **kw)
        # self.logger.debug(f'----------------------------------')
        return result


class AutoLogin(AutoModules):
    login_api = None
    login_params = ['loginname', 'password']

    def __init__(self, user_account, psd):
        super().__init__()
        self.login_form = {
            self.login_params[0]: user_account,
            self.login_params[1]: psd
        }

    def login(self, key='data'):
        result = self.fetch(self.login_api, **{key: self.login_form})
        self.logger.info(f'{"Login Result".center(self.LOG_SPACE_COUNT)}-> {result.text}')
        self.cookies = result.cookies
        return result


class AutoUploadImage(AutoModules):
    upload_img_url = None
    upload_img_file_keys = []
    upload_count = 0

    def create_upload_boundary_img_files(self, file_paths):
        file = Path(file_paths[self.upload_count])
        file_name = file.name
        with file.open('rb') as f:
            file_content = f.read()
        gmt_format = '%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)'
        files = {
            'id': (None, 'WU_FILE_0'),
            'name': (None, file_name),
            'type': (None, 'application/octet-stream'),
            'lastModifiedDate': (None, datetime.now().strftime(gmt_format)),
            'size': (None, str(len(file_content))),
            'file': (file_name, file_content, 'application/octet-stream')
        }
        return files

    def check_file_paths(self, file_paths):
        key_len, paths_len = len(self.upload_img_file_keys), len(file_paths)
        if key_len != paths_len:
            self.logger.warning(f'上传图片的长度与必须的 key 长度不相等: key_len {key_len} != paths_len {paths_len}')
            if key_len > paths_len:
                file_paths.extends(file_paths[-1] * key_len - paths_len)
            else:
                file_paths = file_paths[:key_len]
            raise ValueError(f'上传图片的长度与必须的 key 长度相等: {len(self.upload_img_file_keys)} != {len(file_paths)}')
        for f in map(Path, file_paths):
            if not f.exists():
                raise ValueError(f'文件 {f.name} 不存在')

    def upload_img(self, file_paths):
        self.check_file_paths(file_paths)
        file = Path(file_paths[self.upload_count])
        files = {[self.upload_img_file_keys[self.upload_count]]: (file.name, file.open('rb'))}
        result = self.fetch(self.upload_img_url, files=files)
        self.logger.info(f'{"Upload Img Result".center(self.LOG_SPACE_COUNT)}-> {result.text}')
        return result

    def upload_boundary_img(self, file_paths, **kw):
        self.check_file_paths(file_paths)
        files = self.create_upload_boundary_img_files(file_paths)
        result = self.fetch(self.upload_img_url, files=files, **kw)
        self.logger.info(f'{"Upload Boundary Img Result".center(self.LOG_SPACE_COUNT)}-> {result.text}')
        self.upload_count += 1
        return result


class AutoSubmit(AutoLogin, AutoUploadImage):
    submit_url = None
    submit_params = {}
    submit_img_key = None
    csrf_token = None

    def created(self):
        pass

    def get_csrf_token(self, response):
        m = re.search('name="csrf-token" content="(.*?)"', response.text)
        if m:
            self.csrf_token = m.group(1)

    def check_params(self, params, args):
        args = list(args)
        if len(params) != len(args):
            raise ValueError(f'输入的参数键值对错误！！！ params -> {params}, args -> {args}')
        for i, param in enumerate(params):
            value = args[i]
            self.submit_params[param] = value

    def __init__(self, user_account, psd, params, *args):
        super().__init__(user_account, psd)
        self.check_params(params, args)
        self.created()

    def parse_upload_img_src(self, upload_img_src):
        return upload_img_src

    def get_submit_data(self, upload_img_src):
        data = self.submit_params
        data[self.submit_img_key] = self.parse_upload_img_src(upload_img_src)
        return data

    def submit(self, data, submit_use_json=False):
        if submit_use_json:
            result = self.fetch(self.submit_url, json=data)
        else:
            result = self.fetch(self.submit_url, data=data)
        self.logger.info(f'{"Submit Data".center(self.LOG_SPACE_COUNT)}-> {data}')
        self.logger.info(f'{"Submit Result".center(self.LOG_SPACE_COUNT)}-> {result.text}')
        return result

    def run(self, file_paths):
        self.login()
        self.submit(self.get_submit_data(file_paths))


class AutoOpenBrowserModules(AutoModules):
    driver_find_wait = 10
    By = By

    def __init__(self):
        super().__init__()
        options = self.create_chrome_options()
        self.chrome_options = options
        self.browser = webdriver.Chrome(options=options)

    @staticmethod
    def create_chrome_options():
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors", "enable-automation"])
        options.add_experimental_option("prefs", prefs)
        return options

    def find(self, _id, find_type=By.XPATH, wait=driver_find_wait):
        self.logger.debug(f'----------------------------------')
        self.logger.debug(f'{"Find wait".center(self.LOG_SPACE_COUNT)}-> {wait}')
        self.logger.debug(f'{"Find type".center(self.LOG_SPACE_COUNT)}-> {find_type}')
        self.logger.debug(f'{"Find id".center(self.LOG_SPACE_COUNT)}-> {_id}')
        try:
            method = ec.presence_of_element_located((find_type, _id))
            WebDriverWait(self.browser, wait).until(method)
            return self.browser.find_element(find_type, _id)
        except TimeoutException:
            self.logger.warning(f'获取元素失败 ID -> {_id}')

    def finds(self, _id, find_type=By.XPATH, wait=driver_find_wait):
        self.logger.debug(f'----------------------------------')
        self.logger.debug(f'{"Finds wait".center(self.LOG_SPACE_COUNT)}-> {wait}')
        self.logger.debug(f'{"Finds type".center(self.LOG_SPACE_COUNT)}-> {find_type}')
        self.logger.debug(f'{"Finds id".center(self.LOG_SPACE_COUNT)}-> {_id}')
        try:
            method = ec.presence_of_element_located((find_type, _id))
            WebDriverWait(self.browser, wait).until(method)
            return self.browser.find_elements(find_type, _id)
        except TimeoutException:
            self.logger.warning(f'获取元素失败 ID -> {_id}')

    def fetch(self, url, **kw):
        self.browser.get(url)
        return self

    def wait(self, time: float):
        sleep(time)
        return self

    def __exit__(self):
        self.browser.quit()


class AutoOpenBrowserSubmit(AutoSubmit, AutoOpenBrowserModules):
    __xpath_dict = {}

    def find(self, key, *args):
        return super().find(self.__xpath_dict[key], *args)

    def finds(self, key, *args):
        return super().finds(self.__xpath_dict[key], *args)

    def login(self, _=False):
        self.fetch(self.domain + self.login_api).find('account_input').send_keys(self.login_form[self.login_params[0]])
        self.find('password_input').send_keys(self.login_form[self.login_params[1]])
        self.find('login_submit_button').click()
        return self.wait(1)

    def upload_img(self, file_paths):
        file_path = file_paths[self.upload_count]
        self.find('upload_img').send_keys(file_path)
        return self.wait(1)


class AutoSubmitTemplate(AutoSubmit):
    login_api = '/pc/user/login'
    upload_img_url = '/pc/mark/upload'
    login_params = ['userName', 'password']
    upload_img_file_keys = ['chatUrl', 'chatUrl2', 'refundUrl']
    submit_url = '/pc/mark/save'

    def login(self, key='json'):
        self.headers['token'] = json.loads(super().login(key).text)['data']['token']
        self.update_content_type(None)

    def get_submit_data(self, img_url_list):
        data = self.submit_params
        for i, key in enumerate(self.upload_img_file_keys):
            data[key] = img_url_list[i]
        return data

    def upload_images(self, file_paths):
        url_list = []
        for _ in range(len(file_paths)):
            result = self.upload_boundary_img(file_paths)
            url_list.append(json.loads(result.text)['url'])
        return url_list

    def run(self, file_paths):
        self.login()
        img_url_list = self.upload_images(file_paths)
        self.submit(self.update_content_type('application/json').get_submit_data(img_url_list), True)
