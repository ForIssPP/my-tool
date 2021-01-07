import logging
import os
from importlib import import_module
from pathlib import Path
from time import sleep
from tkinter import filedialog

import requests

from config import mark_param_keys, mark_type_keys, RESTART_INTERVAL, platform_keys
from utils.download import Download

initial_dir = os.getcwd()
file_types = (['png', '*.png'], ['jpg', '*.jpg'], ['gif', '*.gif'])


def choose_img():
    print('请选择要上传的文件')
    return filedialog.askopenfilename(initialdir=initial_dir, title='请选择打标图片', filetypes=file_types)


def choose_upload_img():
    carry_on = input('是否继续添加上传图片？(y/n) n : ')
    if carry_on == 'y' or carry_on == 'Y':
        return choose_img()


def submit(api_key: str, account: str, password: str, *params, auto=True):
    script = getattr(import_module(f'{api_key}.run'), 'Default', None)
    if not script:
        raise ValueError(f'Script {api_key} 不存在')

    file_paths = []
    if auto:
        url = 'http://api.weichabao.co/json/sync/mark/get?token=8bgr0DaspsVvzVgJZqakL&maxAttemptTimes=9999'
        res = requests.get(url).json()
        keys = mark_param_keys['auto']
        params = mark_param_keys[api_key]
        mark_type = mark_type_keys[api_key]
        if res['status'] and res['data']:
            for data in res['data']:
                wwid, content, images = data[keys[0]], data[keys[1]], data[keys[2]]
                instance = script(account, password, params, wwid, mark_type, content)
                while images:
                    file_paths.append(Download(images.pop()).save())
                instance.logger.setLevel(logging.INFO)
                instance.run(file_paths)

    else:
        filename = choose_img()
        if not filename:
            raise ValueError('请至少上传一张图片')

        file_paths.append(filename)
        while len(file_paths) < 3:
            filename = choose_upload_img()
            if filename:
                file_paths.append(filename)
            else:
                break
        instance = script(account, password, *params)
        instance.logger.setLevel(logging.INFO)
        instance.run(file_paths)


def run(account_info_list):
    while True:
        for account_info in account_info_list:
            submit(*account_info)
        sleep(RESTART_INTERVAL)


def parse_account_info(info):
    info[0] = platform_keys[info[0]]
    return info


if __name__ == '__main__':
    import pandas
    account_info_list = pandas.read_csv('../assets/phone.csv').dropna(axis=1).drop_duplicates()
    run(map(parse_account_info, account_info_list.values))
