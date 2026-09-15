#!/usr/bin/env python3
"""Validate a published FastParse Java artifact from Maven Central."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
import textwrap
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

GROUP_ID = "io.github.natan-sysview"
ARTIFACT_ID = "fastparse"
METADATA_URL = "https://repo1.maven.org/maven2/io/github/natan-sysview/fastparse/maven-metadata.xml"

PROGRAM = r'''
import dev.fastparse.FastParseClient;
import dev.fastparse.FastParseField;
import dev.fastparse.FastParseFormat;
import dev.fastparse.ParseOptions;
import dev.fastparse.ParseResult;

public class App {
  public static void main(String[] args) throws Exception {
    try (FastParseClient parser = FastParseClient.open()) {
      ParseOptions options = ParseOptions.builder()
          .format(FastParseFormat.JSON)
          .includeRules("method_declaration")
          .fields(FastParseField.RULE, FastParseField.TEXT, FastParseField.BYTE_RANGE)
          .build();
      ParseResult result = parser.parseText("class Demo { void run() { System.out.println(\"maven\"); } }", options);
      String json = result.asUtf8String();
      if (result.getNodeCount() != 1 || !json.contains("method_declaration")) {
        throw new IllegalStateException("published Maven JSON smoke failed: " + json);
      }
      ParseResult diagnostics = parser.parseText(
          "class Demo { void broken( { }",
          ParseOptions.builder().format(FastParseFormat.DIAGNOSTICS).build());
      String quality = diagnostics.asUtf8String();
      if (!quality.contains("\"hasErrors\":true") || quality.contains("\"nodes\"")) {
        throw new IllegalStateException("published Maven diagnostics smoke failed: " + quality);
      }
      System.out.println("FastParse published Maven smoke OK");
      System.out.println(parser.version());
      System.out.println(parser.loadedCorePath());
    }
  }
}
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FastParse from Maven Central.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    parser.add_argument("--interval-seconds", type=int, default=30)
    return parser.parse_args()


def published_versions() -> set[str]:
    try:
        with urllib.request.urlopen(METADATA_URL, timeout=20) as response:
            root = ET.fromstring(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return set()
        raise
    return {node.text for node in root.findall("./versioning/versions/version") if node.text}


def wait_for_version(version: str, timeout_seconds: int, interval_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        if version in published_versions():
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{GROUP_ID}:{ARTIFACT_ID}:{version} was not indexed by Maven Central")
        print(f"Waiting for {GROUP_ID}:{ARTIFACT_ID}:{version} to be indexed by Maven Central...", flush=True)
        time.sleep(interval_seconds)


def maven_command() -> str:
    candidates = ["mvn.cmd", "mvn"] if os.name == "nt" else ["mvn"]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise FileNotFoundError(
        "Maven executable not found on PATH. Expected mvn.cmd or mvn on Windows, mvn on Unix."
    )


def run(command: list[str], cwd: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(command, cwd=str(cwd), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}")
    return completed.stdout


def main() -> int:
    args = parse_args()
    wait_for_version(args.version, args.timeout_seconds, args.interval_seconds)
    with tempfile.TemporaryDirectory(prefix="fastparse-published-maven-") as temp:
        project = Path(temp) / "consumer"
        (project / "src/main/java").mkdir(parents=True)
        (project / "pom.xml").write_text(textwrap.dedent(f'''
            <?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0"
                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                     xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
              <modelVersion>4.0.0</modelVersion>
              <groupId>dev.fastparse.smoke</groupId>
              <artifactId>fastparse-smoke</artifactId>
              <version>1.0.0</version>
              <properties>
                <maven.compiler.source>1.8</maven.compiler.source>
                <maven.compiler.target>1.8</maven.compiler.target>
                <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
              </properties>
              <dependencies>
                <dependency>
                  <groupId>{GROUP_ID}</groupId>
                  <artifactId>{ARTIFACT_ID}</artifactId>
                  <version>{args.version}</version>
                </dependency>
              </dependencies>
              <build>
                <plugins>
                  <plugin>
                    <groupId>org.codehaus.mojo</groupId>
                    <artifactId>exec-maven-plugin</artifactId>
                    <version>3.5.0</version>
                    <configuration><mainClass>App</mainClass></configuration>
                  </plugin>
                </plugins>
              </build>
            </project>
        ''').lstrip(), encoding="utf-8")
        (project / "src/main/java/App.java").write_text(PROGRAM, encoding="utf-8")
        env = os.environ.copy()
        env.pop("FASTPARSE_LIBRARY_PATH", None)
        env.pop("TSMP_LIBRARY_PATH", None)
        out = run([maven_command(), "-q", "compile", "exec:java"], project, env)
        if "FastParse published Maven smoke OK" not in out:
            raise AssertionError(f"published Maven smoke failed:\n{out}")
        print(out)
    print(f"Validated published Maven package: {GROUP_ID}:{ARTIFACT_ID}:{args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
