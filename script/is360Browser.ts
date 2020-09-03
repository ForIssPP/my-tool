/**
 * 检查是否为360浏览器的ES5函数
 */
export default function is360Browser() {
  const ua = navigator.userAgent.toLowerCase();

  if (/chrome/.test(ua)) {
    const { mimeTypes } = navigator;
    const { length } = mimeTypes;
    const NOW_CHROME_BROWSER_MAX_MIME_TYPES_LENGTH = 4;
    const NOW_360_BROWSER_REQUIRED_HAS_MIME_TYPE_NAME = 'application/x-pnacl';

    if (length <= NOW_CHROME_BROWSER_MAX_MIME_TYPES_LENGTH) {
      return false;
    }

    for (const mimeType of mimeTypes) {
      console.log(mimeType.type);
      if (mimeType.type === NOW_360_BROWSER_REQUIRED_HAS_MIME_TYPE_NAME) {
        return true;
      }
    }
  }

  return false;
}
