# Naming

The product name is **FastParse**.

The original lab name was TSMP. Some internal files, enum names, and compatibility symbols still use `tsmp` to avoid breaking existing tests and bindings.

## Public Branding

Use FastParse in user-facing docs, examples, packages, and future bindings.

Recommended native artifact names:

```text
macOS   libfastparse.dylib
Linux   libfastparse.so
Windows fastparse.dll
```

Recommended public C entry points:

```c
fastparse_version
fastparse_parse
fastparse_result_free
```

## Compatibility

The legacy TSMP ABI remains available:

```c
tsmp_version
tsmp_parse
tsmp_result_free
```

Both sets of functions call the same implementation.

Bindings should prefer `fastparse_*` when available and fall back to `tsmp_*` only for older native libraries.

## Headers

Preferred header:

```c
#include "fastparse.h"
```

Compatibility header:

```c
#include "tsmp.h"
```

`fastparse.h` currently includes `tsmp.h`, so the existing `TsmpOptions`, `TsmpResult`, and `TSMP_*` constants remain the shared ABI types.

## Python

Preferred import:

```python
from fastparse import FastParse
```

Compatibility import:

```python
from tsmp import Tsmp
```
