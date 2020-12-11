from utils.auto_submit import AutoSubmitTemplate


class Default(AutoSubmitTemplate):
    domain = 'https://dianshangdanao.com/'


if __name__ == '__main__':
    req = Default(
        '123456', '123456',  markName='tb043043909', remark='刷单 给他返款了 隔了两天就是 淘宝上退款',
        markType=1,
    )
    req.run([r'C:\Users\Lenovo\Desktop\1.gif'])
