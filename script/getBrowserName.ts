import is360Browser from './is360Browser';

/**
 * 使用 userAgent 获取当前国内常用浏览器的名称
 */
export default function getBrowserName() {
  let browserType;
  const ua = navigator.userAgent.toLowerCase();
  const BROWSER_NAMES = [
    'IE',
    'Firefox',
    'UC',
    'Opera',
    'Baidu',
    'Sougou',
    'Liebao',
    '123',
    '2345',
    'QQ',
    'Safari',
    'Chrome',
    '360'
  ];
  const browserRegExps = [
    [/msie/, /trident/],
    /firefox/,
    /ubrowser/,
    /opera/,
    /bidubrowser/,
    /metasr/,
    /lbbrowser/,
    /you123/,
    /2345/,
    [/tencenttraveler/, /qqbrowse/],
    /safari/,
    /chrome/,
    { test: is360Browser }
  ];

  browserRegExps.forEach((re, index) => {
    if (re instanceof Array) {
      if (re.some(r => r.test(ua))) {
        browserType = BROWSER_NAMES[index];
      }
    } else {
      if (re.test(ua)) {
        browserType = BROWSER_NAMES[index];
      }
    }
  });

  return browserType;
}
