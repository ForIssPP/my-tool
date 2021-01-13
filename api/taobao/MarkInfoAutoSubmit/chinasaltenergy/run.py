import json
from pathlib import Path
from time import sleep
import pandas
from random import randint
from utils.auto_submit import AutoModules


class Default(AutoModules):
    domain = 'https://h5.gas.chinasaltenergy.com'
    config_path = Path('../assets/config.json')
    last_count = json.loads(config_path.read_text())['last_count']

    def run(self, user_phone_no: str):
        # invitation_code = 'XhST6K'
        # invitation_code = '5lU55n'
        invitation_code = 'jvu3ei'
        self.update_content_type('application/json;charset=UTF-8')
        return self.fetch('/mp/api/channelagent/channelinviteuser/newUserNC', json={
            "userPhoneNo": user_phone_no, "invitationCode": invitation_code
        })

    def send(self, phone):
        if not config_path.exists():
            config_path.write_text('{"last_count": 0}')

        self.logger.info(f'正在提交第 {self.last_count + 1} 个 电话为: {phone}')
        self.last_count += 1
        self.logger.info(f'提交结果 -> {self.run(phone).text}')
        self.config_path.write_text(json.dumps({'last_count': self.last_count}))
        # sleep_time = randint(1, 1)
        # module.logger.info(f'暂停 {sleep_time} 秒继续')
        # sleep(sleep_time)


if __name__ == '__main__':
    config_path = Path('../assets/config.json')
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
    try:
        splice_count = ''
        if is_csv:
            for [phone] in phones.values[module.last_count:module.last_count + today_upload_count]:
                module.send(phone)

        else:
            for i, phone in enumerate(phones[module.last_count:module.last_count + today_upload_count]):
                module.send(phone)

    except Exception as err:
        module.logger.exception(err)
        module.logger.info(f'在提交第 {module.last_count} 个时失败')
