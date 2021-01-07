import json
from pathlib import Path
from time import sleep

from utils.auto_submit import AutoModules


class Default(AutoModules):
    domain = 'https://h5.gas.chinasaltenergy.com'

    def run(self, user_phone_no: str):
        # XhST6K
        self.update_content_type('application/json;charset=UTF-8')
        return self.fetch('/mp/api/channelagent/channelinviteuser/newUserNC', json={
            "userPhoneNo": user_phone_no, "invitationCode": "5lU55n"
        })


if __name__ == '__main__':
    # import pandas
    from random import randint

    config_path = Path('../data/config.json')
    today_upload_count = int(input('请输入个数： '))

    if not config_path.exists():
        config_path.write_text('{"last_count": 0}')

    if str(today_upload_count)[-1] == '0':
        today_upload_count += randint(1, 9)

    with Path('../data/phone.txt').open('r') as file:
        phones = file.read().split('\n')

    module = Default()
    module.logger.setLevel('INFO')
    last_count = json.loads(config_path.read_text())['last_count']
    try:
        for i, phone in enumerate(phones[last_count:last_count + today_upload_count]):
            module.logger.info(f'正在提交第 {last_count + 1} 个')
            last_count += 1
            module.logger.info(f'提交结果 -> {module.run(phone).text}')
            config_path.write_text(json.dumps({'last_count': last_count}))
            # sleep_time = randint(1, 1)
            # module.logger.info(f'暂停 {sleep_time} 秒继续')
            # sleep(sleep_time)
    except Exception as err:
        module.logger.exception(err)
        module.logger.info(f'在提交第 {last_count} 个时失败')
