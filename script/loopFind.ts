type QueryHandler = (id: string) => NodeListOf<Element>;

interface LoopFindOption {
  time?: number;
  maxErrorCount?: number;
}

interface LoopFindError {
  name: string;
  message: string;
  option: LoopFindOption;
}

export default class LoopFind {
  private _errorCount: number = 0;

  private _query: QueryHandler;

  option: LoopFindOption = {
    time: 100,
    maxErrorCount: 10,
  };

  constructor(
    query: QueryHandler = id => document.querySelectorAll(id),
    option: LoopFindOption
  ) {
    this._query = query;
    this.option = {
      ...this.option,
      ...option,
    };
  }

  private _find(
    id: string,
    resolve: (value: NodeList) => void,
    reject: (error: LoopFindError) => void
  ) {
    const findEl = this._query(id);
    if (findEl?.length) return resolve(findEl);

    if (this._errorCount === this.option.maxErrorCount)
      return reject({
        name: id,
        message: '[LoopFindError]: 超出错误上限',
        option: this.option,
      });

    this._errorCount++;
    setTimeout(this._find.bind(this), this.option.time, id, resolve, reject);
  }

  run(id: string) {
    return new Promise<NodeList>((resolve, reject) =>
      this._find(id, resolve, reject)
    );
  }
}
