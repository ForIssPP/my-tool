interface SocketsEventMap extends WebSocketEventMap {}

interface Sockets extends WebSocket {}

/**
 * 封装 Websocket API, 具有高度的可扩展性
 */
class Sockets extends WebSocket {
  constructor(url: string, protocols?: string | string[]) {
    super(url, protocols);
    this.init();
  }

  init() {
    const DEFAULT_LOG_MESSALGE = '[LOG] Message ->';
    const DEFAULT_ERROR_MESSALGE = '[ERROR] Error ->';

    this.on('open', () => console.log(DEFAULT_LOG_MESSALGE, 'Ws is open'))
      .on('close', () => console.log(DEFAULT_LOG_MESSALGE, 'Ws is close'))
      .on('error', error => console.error(DEFAULT_ERROR_MESSALGE, error))
      .on('message', evt => console.log(DEFAULT_LOG_MESSALGE, evt.data));
  }

  on<K extends keyof SocketsEventMap>(eventType: K, listener: (this: Sockets, ev: SocketsEventMap[K]) => any) {
    this.addEventListener(eventType, listener.bind(this));
    return this;
  }
}

export default Sockets;
