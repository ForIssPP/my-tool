import logging
import os
from importlib import import_module
from pathlib import Path
from tkinter import filedialog

initial_dir = os.getcwd()
file_types = (['png', '*.png'], ['jpg', '*.jpg'], ['gif', '*.gif'])


def choose_img():
    print('请选择要上传的文件')
    return filedialog.askopenfilename(initialdir=initial_dir, title='请选择打标图片', filetypes=file_types)


def choose_upload_img():
    carry_on = input('是否继续添加上传图片？(y/n) n : ')
    if carry_on == 'y' or carry_on == 'Y':
        return choose_img()


def run(*args):
    file_paths = []
    # filename = choose_img()
    filename = '/Users/siykt/Desktop/7689814814815.png'
    if not filename:
        print('请至少上传一张图片')
        return run(*args)

    file_paths.append(filename)
    # while len(file_paths) < 3:
    #     filename = choose_upload_img()
    #     if filename:
    #         file_paths.append(filename)
    #     else:
    #         break

    script = getattr(import_module(f'{args[0]}.run'), 'Default', None)
    if script:
        instance = script(*args[1:])
        instance.logger.setLevel(logging.INFO)
        instance.run(file_paths)


mark_param_keys = {
    '91laihama': ['wang', 'jbtype', 'remark'],
    'chadianshang': ['markName', 'markType', 'remark'],
    'dianshangdanao': ['markName', 'markType', 'remark'],
    'dshangyan': ['markName', 'markType', 'remark'],
    'qinchacha': ['nick', 'type_id', 'content'],
}

mark_type_keys = {
    '91laihama': '跑单,敲诈,',
    'chadianshang': 1,
    'dianshangdanao': 1,
    'dshangyan': 1,
    'qinchacha': 1,
}

if __name__ == '__main__':
    # https://img.weichabao.com/blacklist/rep/2021/1/6/1270983367627
    # key = '91laihama'
    # key = 'dianshangdanao'
    key = 'qinchacha'
    # psd = 'siykt749851'
    # psd = 'iUKKjssciYnQ4.u'
    psd = 'QC8BwkQ2PCSqYSN'
    params = ['爱你龙宝22977725', mark_type_keys[key], '骗我199元 伤心 别的不说了 祝你在新的一年里买药不够 自己再多添点 我这也当是给你水滴筹啦吧 做好事积德']
    run(key, '13110790527', psd, mark_param_keys[key], *params)
