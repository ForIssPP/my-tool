import logging
from pathlib import Path

import win32ui
import fire
from importlib import import_module


def choose_img():
    dlg = win32ui.CreateFileDialog(1)
    dlg.SetOFNInitialDir(str(Path('.').absolute()))
    dlg.DoModal()
    return dlg.GetPathName()


def choose_upload_img():
    carry_on = input('是否继续添加上传图片？(y/n) n : ')
    if carry_on == 'y' or carry_on == 'Y':
        return choose_img()


def run(*args):
    file_paths = []
    print('请选择要上传的文件')
    filename = choose_img()
    if not filename:
        print('请至少上传一张图片')
        return run(*args)
    file_paths.append(filename)
    while len(file_paths) < 3:
        filename = choose_upload_img()
        if filename:
            file_paths.append(filename)
        else:
            break

    script = getattr(import_module(f'{args[0]}.run'), 'Default', None)
    instance = script(*args[1:-1], **args[-1])
    # instance.logger.setLevel(logging.INFO)
    instance.run(file_paths)


if __name__ == '__main__':
    fire.Fire(run)
