from utils.auto_submit import AutoOpenBrowserModules, AutoSubmit


class Default(AutoSubmit, AutoOpenBrowserModules):
    domain = 'http://www.maijiabashi.com/'
    login_api = '/user/login.htm'
    submit_url = '/publictool.htm?accessurl=account_validate.htm'
    __xpath_dict = dict(
        account_input="input[@id='normal']",
        password_input="input[@id='PassWord']",
        toggle_password_login="//form[@id='plogin_form']/dd[@class='remember']/div[@class='right switch-login-type']",
        login_submit_button="//form[@id='login_form']/dd[@class='commit']/input",
        upload_img='//*[@id="upload"]',
        mark_type="//p[@id='selectTypeBox']/label[@class='fs-14 cl000']",
        mark_account="//input[@id='nick']",
        mark_content="//textarea[@id='nickContent']",
        mark_submit="//span[@id='addAccusationBtn']",
    )

    def find(self, key, *args):
        return super().find(self.__xpath_dict[key], *args)

    def finds(self, key, *args):
        return super().finds(self.__xpath_dict[key], *args)

    def login(self, _=False):
        self.fetch(self.domain + self.login_api).wait(1).find('toggle_password_login').click()
        self.find('account_input').send_keys(self.login_form[self.login_params[0]])
        self.find('password_input').send_keys(self.login_form[self.login_params[1]])
        self.find('login_submit_button').click()
        return self.wait(1)

    def upload_img(self, file_paths):
        file_path = file_paths[self.upload_count]
        self.find('upload_img').send_keys(file_path)
        return self.wait(1)

    def submit(self, data=None, submit_use_json=False):
        self.fetch(self.domain + self.submit_url).finds('mark_type')[self.submit_params['type_id']].click()
        self.find('mark_account').send_keys(self.submit_params['nick'])
        self.find('mark_content').send_keys(self.submit_params['content'])
        self.find('mark_submit').click()
        return self.wait(1)

    def run(self, file_paths):
        self.login()
        self.upload_img(file_paths)
        self.submit().print_result()


if __name__ == '__main__':
    mark_type = dict(
        违规=0,
        降权=1,
        差评=2,
        退单=3,
        骗子=4,
        其他=5,
    )
    req = Default(
        '123456', '123456',  nick='tb043043909', type_id=mark_type['骗子'],
        content='刷单 给他返款了 隔了两天就是 淘宝上退款'
    )
    req.run([r'C:\Users\Lenovo\Desktop\666.png'])
