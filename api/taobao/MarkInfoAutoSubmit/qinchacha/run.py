from utils.auto_submit import AutoOpenBrowserModules, AutoSubmit


class Default(AutoSubmit, AutoOpenBrowserModules):
    domain = 'https://www.qinchacha.com'
    login_api = '/home/index/v/login'
    __xpath_dict = dict(
        # login
        login_form="//div[@class='regist_div']/div[@class='input_bg']//input",
        login_submit_button="//div[@class='button-bot']",
        # upload
        upload_img='//*[@id="input_file"]',
        # mark
        open_mark_button="//div[@class='main-home-search-button-all flex-over-center']",
        mark_account="//div[@class='dialog']/div[@class='dialog_sign_wangwang']/div[1]/input",
        mark_search="//div[@class='dialog']/div[@class='dialog_sign_wangwang']/div[1]/div[@class='flex-over-center']",
        mark_type="//div[@class='dialog_sign_wangwang']/div[2]/div[@class='flex-over-center']//span",
        mark_content="//textarea",
        mark_submit="//div[@class='dialog']//div[@class='flex-over-center']/div[@class='flex-over-center']",
        result="//div[@class='layui-layer-content']",
    )

    def find(self, key, *args):
        return super().find(self.__xpath_dict[key], *args)

    def finds(self, key, *args):
        return super().finds(self.__xpath_dict[key], *args)

    def login(self, _=False):
        form = self.fetch(self.domain + self.login_api).finds('login_form')
        for i, input_elm in enumerate(form):
            input_elm.send_keys(self.login_form[self.login_params[i]])
        self.find('login_submit_button').click()
        return self.print_result().wait(1).fetch(self.domain)

    def upload_img(self, file_paths):
        file_path = file_paths[self.upload_count]
        self.find('upload_img').send_keys(file_path)
        return self.wait(1)

    def submit(self, data=None, submit_use_json=False):
        self.find('mark_account').send_keys(self.submit_params['nick'])
        self.find('mark_search').click()
        self.print_result().find('mark_submit').click()
        return self.wait(1)

    def print_result(self):
        try:
            self.logger.info(f"{'Runtime Result'.center(self.LOG_SPACE_COUNT)}-> {self.find('result').text}")
        except:
            pass
        return self

    def run(self, file_paths):
        self.browser.execute_script("arguments[0].click()", self.login().find('open_mark_button'))
        self.finds('mark_type')[self.submit_params['type_id']].click()
        self.upload_img(file_paths).find('mark_content').send_keys(self.submit_params['content'])
        self.submit().print_result()


if __name__ == '__main__':
    mark_type = dict(
        恶意打假=0,
        恶意退款=1,
        恶意差评=2,
        抽检=3,
        评价广告=4,
        补单返利=5,
        降权号=6,
    )
    req = Default(
        '123456', '123456',  nick='tb043043909', type_id=mark_type['恶意退款'],
        content='刷单 给他返款了 隔了两天就是 淘宝上退款'
    )
    req.run([r'C:\Users\Lenovo\Desktop\666.png'])
    req.__exit__()
