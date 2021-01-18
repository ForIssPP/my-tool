import json
from pathlib import Path
from time import sleep
import pandas
from random import randint
from utils.auto_submit import AutoModules
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

config_path = Path('../assets/config.json')


class Default(AutoModules):
    domain = 'https://h5.gas.chinasaltenergy.com'
    config_path = Path('../assets/config.json')
    last_count = json.loads(config_path.read_text())['last_count']

    def __init__(self):
        super(Default, self).__init__()

    def run(self, user_phone_no: str):
        # invitation_code = 'XhST6K'
        # invitation_code = '5lU55n'
        # invitation_code = 'jvu3ei'
        # invitation_code = 'z497sw'
        # invitation_code = '5lU55n'
        invitation_code = '1xusdt'
        self.update_content_type('application/json;charset=UTF-8')
        return self.fetch('/mp/api/channelagent/channelinviteuser/newUserNC', json={
            "userPhoneNo": user_phone_no, "invitationCode": invitation_code
        })

    def send(self, phone):
        if not config_path.exists():
            config_path.write_text('{"last_count": %d}' % self.last_count)

        self.logger.info(f'正在提交第 {self.last_count + 1} 个 电话为: {phone}')
        self.last_count += 1
        self.logger.info(f'提交结果 -> {self.run(phone).text}')
        self.config_path.write_text(json.dumps({'last_count': self.last_count}))
        sleep_time = randint(5, 15)
        self.logger.info(f'暂停 {sleep_time} 秒继续')
        sleep(sleep_time)


def main():
    # today_upload_count = 1
    today_upload_count = int(input('请输入个数： '))

    if str(today_upload_count)[-1] == '0':
        today_upload_count += randint(1, 9)

    # with Path('../assets/phone.csv').open('r') as file:
    #     phones = file.read().split('\n')
    phones = pandas.read_csv('../assets/phone.csv').dropna(axis=1).drop_duplicates()
    is_csv = True

    module = Default()
    module.logger.setLevel('INFO')
    executor = ThreadPoolExecutor(max_workers=10)

    try:
        splice_count = ''
        if is_csv:
            tasks = []

            for [phone] in phones.values[module.last_count:module.last_count + today_upload_count]:
                tasks.append(executor.submit(module.send, phone))
                # module.send(phone)

            wait(tasks, return_when=ALL_COMPLETED)
            module.logger.info('提交完毕')

        else:
            for i, phone in enumerate(phones[module.last_count:module.last_count + today_upload_count]):
                module.send(phone)

    except Exception as err:
        module.logger.exception(err)
        module.logger.info(f'在提交第 {module.last_count} 个时失败')


if __name__ == '__main__':
    main()
