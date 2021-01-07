import logging
import os
from importlib import import_module
from time import sleep
from tkinter import filedialog
import requests
from config import mark_param_keys, mark_type_keys, RESTART_INTERVAL, platform_keys, API_URL
from utils.download import Download
import pandas

logging.getLogger().setLevel(logging.INFO)
initial_dir = os.getcwd()
file_types = (['png', '*.png'], ['jpg', '*.jpg'], ['gif', '*.gif'])


def choose_img():
    print('请选择要上传的文件')
    return filedialog.askopenfilename(initialdir=initial_dir, title='请选择打标图片', filetypes=file_types)


def choose_upload_img():
    carry_on = input('是否继续添加上传图片？(y/n) n : ')
    if carry_on == 'y' or carry_on == 'Y':
        return choose_img()


def get_script(api_key):
    script = getattr(import_module(f'{api_key}.run'), 'Default', None)
    if not script:
        raise ValueError(f'Script {api_key} 不存在')
    return script


def fetch_local_file_paths():
    filename = choose_img()
    if not filename:
        raise ValueError('请至少上传一张图片')

    file_paths = [filename]
    while len(file_paths) < 3:
        filename = choose_upload_img()
        if filename:
            file_paths.append(filename)
        else:
            break
    return file_paths


def fetch_api_mark_info():
    url = API_URL
    res = requests.get(url).json()
    # script = get_script(api_key)
    if res['status'] and res['data']:
        return res


def submit(api_key: str, account: str, password: str, file_paths: list[str], *params):
    script = getattr(import_module(f'{api_key}.run'), 'Default', None)
    if not script:
        raise ValueError(f'Script {api_key} 不存在')

    instance = script(account, password, *params)
    instance.logger.setLevel(logging.INFO)
    instance.logger.info(f'开始提交{api_key}平台...')
    instance.run(file_paths)
    instance.logger.info(f'{api_key}平台提交成功')


def run(account_info_list, auto_mark=True):
    while True:
        if auto_mark:
            res = fetch_api_mark_info()
            keys = mark_param_keys['auto']
            for data in res['data']:
                wwid, content, images = data[keys[0]], data[keys[1]], data[keys[2]]
                file_paths = []
                while images:
                    file_paths.append(Download(images.pop()).save())
                for info in account_info_list:
                    if info.all():
                        api_key = info[0]
                        submit(*info, file_paths, mark_param_keys[api_key], wwid, mark_type_keys[api_key], content)
        else:
            for api_key, account, psd in account_info_list:
                submit(api_key, account, psd, fetch_local_file_paths())
        logging.info(f'开始等待 {RESTART_INTERVAL}s️... ')
        sleep(RESTART_INTERVAL)


def parse_account_info(info):
    platform = info[0]
    if platform in platform_keys:
        info[0] = platform_keys[platform]
    else:
        logging.warning(f'存在未添加的平台: {platform}')
        info[0] = None
    return info


if __name__ == '__main__':
    run(list(map(parse_account_info, pandas.read_csv('./assets/account_info.csv').dropna(axis=1).values)))
