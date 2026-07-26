export class FastParseError extends Error {
  readonly nativeStatus: number;
  readonly resultStatus: number;

  constructor(message: string, nativeStatus = 0, resultStatus = 0) {
    super(message);
    this.name = "FastParseError";
    this.nativeStatus = nativeStatus;
    this.resultStatus = resultStatus;
  }
}

export class NativeLoadError extends FastParseError {
  readonly searchedPaths: string[];

  constructor(message: string, searchedPaths: string[]) {
    super(message);
    this.name = "NativeLoadError";
    this.searchedPaths = searchedPaths;
  }
}
