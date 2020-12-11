from utils.auto_submit import AutoSubmit


class Default(AutoSubmit):
    domain = 'http://wang.91laihama.com'
    upload_img_url = '/Fenzhan/UpFile?type=1'
    login_api = '/Login/SaveLogin'
    submit_url = '/wang/JbWang'
    upload_img_file_keys = ['fileurl1']
    submit_img_key = 'imgurl'

    def parse_upload_img_src(self, upload_img_src):
        return "|".join(upload_img_src)


if __name__ == '__main__':
    req = Default(
        '123456', '123456', wang='tb043043909', jbtype='跑单,敲诈,',
        remark='刷单 给他返款了 隔了两天就是 淘宝上退款', imgurl=None
    )
    req.run([r'C:\Users\Lenovo\Desktop\666.png'])
