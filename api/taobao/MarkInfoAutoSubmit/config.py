# 打标参数名
mark_param_keys = {
    '91laihama': ['wang', 'jbtype', 'remark'],
    'chadianshang': ['markName', 'markType', 'remark'],
    'dianshangdanao': ['markName', 'markType', 'remark'],
    'dianshangyan': ['markName', 'markType', 'remark'],
    'qinchacha': ['nick', 'type_id', 'content'],
    'auto': ['wwid', 'experience', 'imgs']
}
# 打标平台
platform_keys = {
    '癞蛤蟆': '91laihama', '查电商': 'chadianshang', '电商大脑': 'dianshangdanao', '电商眼': 'dianshangyan', '亲查查': 'qinchacha'
}
# 打标类型
mark_type_keys = {'91laihama': '跑单,敲诈,', 'chadianshang': 1, 'dianshangdanao': 1, 'dianshangyan': 1, 'qinchacha': 1, }
# 重启间隔(单位秒)
RESTART_INTERVAL = 60 * 10
API_URL = 'http://api.weichabao.com/json/sync/mark/get?token=8bgr0DaspsVvzVgJZqakL&maxAttemptTimes=9999'
