# Java Parse String Example

Compile the Java binding classes and run this example against explicit local native paths:

```bash
cd /Users/natanbarronlugo/Desktop/Proyectos/fast_parser
python3 scripts/build_java_jni.py
mkdir -p /tmp/fastparse-java-example
javac --release 8 \
  -d /tmp/fastparse-java-example \
  $(find bindings/java/fastparse/src/main/java -name '*.java') \
  examples/java/01_parse_string/ParseStringExample.java
java -cp /tmp/fastparse-java-example ParseStringExample \
  "$PWD/bin/libfastparse.dylib" \
  "$PWD/bin/libfastparse_jni.dylib"
```

The source is passed as a Java `String`, encoded to bytes in memory, and FastParse returns JSON bytes in JVM-owned memory.
