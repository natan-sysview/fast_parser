# FastParse Java Binding

JNI Java binding for the FastParse native C ABI.

Current status: first Java binding implementation for local/package validation.

## Maven coordinates

Until FastParse owns a dedicated domain namespace, Maven Central publication uses the GitHub-backed namespace:

```xml
<dependency>
  <groupId>io.github.natan-sysview</groupId>
  <artifactId>fastparse</artifactId>
  <version>0.1.2</version>
</dependency>
```

Java package names remain FastParse-branded:

```java
import dev.fastparse.FastParseClient;
```

## Java version

The public API targets Java 8+ (`maven.compiler.source=1.8` / `maven.compiler.target=1.8`). JNI is used instead of Panama so users are not forced onto a modern JDK.

## Native loading contract

Normal package-manager installs should bundle native resources for each supported RID. The loader expects:

```text
/dev/fastparse/native/<rid>/libfastparse.dylib
/dev/fastparse/native/<rid>/libfastparse_jni.dylib
/dev/fastparse/native/<rid>/libfastparse.so
/dev/fastparse/native/<rid>/libfastparse_jni.so
/dev/fastparse/native/<rid>/fastparse.dll
/dev/fastparse/native/<rid>/fastparse_jni.dll
```

Supported RIDs:

- `windows-x64`
- `linux-x64`
- `macos-x64`
- `macos-arm64`

Advanced users can pass explicit paths:

```java
try (FastParseClient client = FastParseClient.open(coreLibraryPath, jniLibraryPath)) {
    // parse in RAM
}
```

The parser itself does not create temporary source files. The Java loader may extract bundled native libraries to a JVM temp/cache directory once so `System.load(...)` can load them.

## Minimal parse example

```java
import dev.fastparse.FastParseClient;
import dev.fastparse.ParseOptions;
import dev.fastparse.ParseResult;

public class App {
  public static void main(String[] args) {
    try (FastParseClient client = FastParseClient.open()) {
      String javaSource = "class Hello { void run() {} }";
      ParseResult result = client.parseText(javaSource, ParseOptions.builder().build());
      System.out.println(client.version());
      System.out.println(result.getNodeCount());
      System.out.println(result.asUtf8String());
    }
  }
}
```

## COBOL extension example

```java
client.loadLanguageExtension("/path/to/libfastparse_language_cobol.dylib");
ParseResult result = client.parseText(
    "      IDENTIFICATION DIVISION.\n      PROGRAM-ID. HELLO.\n",
    ParseOptions.builder().language("cobol").build());
```

Load language extensions before starting worker threads.

## Threading contract

- Native parse calls are intended to be thread-safe per call.
- Use one `FastParseClient` per worker unless the application has validated shared-client behavior.
- Load all language extensions before concurrent parsing begins.
- Parent application owns file IO, queues, and database writes.

## Output formats

- JSON: UTF-8 text AST.
- CSV: UTF-8 tabular rows.
- STATS: compact native stats payload as UTF-8 text/JSON depending on native version.
- BINARY: binary MessagePack AST; do not treat it as text.
- DIAGNOSTICS: parse-quality payload with Tree-sitter error/missing information.


## Release pipeline

The Maven Central artifact is assembled by GitHub Actions from:

- the FastParse core native archives: `fastparse-<version>-<platform>-<arch>`
- the Java JNI bridge archives: `fastparse-java-jni-<version>-<platform>-<arch>`
- the Java API sources under `bindings/java/fastparse`

Publishing uses the Maven Central Portal plugin with token credentials and GPG signing.
Required GitHub repository secrets:

- `CENTRAL_USERNAME`
- `CENTRAL_PASSWORD`
- `GPG_PRIVATE_KEY` with the full ASCII-armored private key, or `GPG_PRIVATE_KEY_B64` with the base64-encoded ASCII-armored private key
- `GPG_PASSPHRASE`

Recommended private-key export for GitHub Actions:

```bash
gpg --armor --export-secret-keys <KEY_ID> > fastparse-maven-private-key.asc
pbcopy < fastparse-maven-private-key.asc
```

The copied value must start with `-----BEGIN PGP PRIVATE KEY BLOCK-----` and end with `-----END PGP PRIVATE KEY BLOCK-----`.
Do not paste the public key, Maven XML, or a Maven Central token into `GPG_PRIVATE_KEY`.

Alternative base64 form:

```bash
gpg --armor --export-secret-keys <KEY_ID> | base64 | pbcopy
```

Paste that value into `GPG_PRIVATE_KEY_B64`.

Publishing is intentionally gated by the repository variable:

- `MAVEN_PUBLISH=true`

Without that variable, CI still builds and validates the Maven package, but it does not publish to Maven Central.
