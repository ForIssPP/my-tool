/**
 * 使用 async + Promise 实现的简单的 sleep 函数
 * @param time 等待时间
 */
export default async function sleep(time: number): Promise<true> {
  await new Promise(resolve => setTimeout(resolve, time));
  return true;
}
