#!/usr/bin/env python3
"""Find likely framework false negatives by comparing text evidence with captures."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT.parents[1]
DEFAULT_DB = LAB_ROOT / "inventory" / "parser_lab_inventory.sqlite"
DEFAULT_SOURCE_ROOT = Path("/Users/natanbarronlugo/Desktop/Proyectos/mifel/fuentes/meta")
DEFAULT_QUERY = ROOT / "queries" / "frameworks.scm"
DEFAULT_JSON = ROOT / "audits" / "framework_false_negative_audit.json"
DEFAULT_REPORT = ROOT / "audits" / "framework_false_negative_audit.md"
CAPTURE_RE = re.compile(r"capture:\s+\d+\s+-\s+(?P<capture>[\w.]+),")


FAMILY_PATTERNS: dict[str, list[str]] = {
    "spring": [
        r"\borg\.springframework\.",
        r"@\s*(SpringBootApplication|RestController|Controller|Service|Repository|Component|Autowired|Bean|Configuration|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|ControllerAdvice|RestControllerAdvice|ExceptionHandler|PathVariable|RequestBody|ResponseBody|Primary|Scope|Async|EnableAsync|SpringBootTest|Validated|Transactional)\b",
        r"\b(SpringApplication|RestTemplate|Jaxb2Marshaller|JdbcTemplate|NamedParameterJdbcTemplate)\b",
    ],
    "security": [
        r"\borg\.springframework\.security\.",
        r"@\s*(PreAuthorize|PostAuthorize|Secured|EnableWebSecurity|EnableGlobalMethodSecurity|WithMockUser)\b",
    ],
    "jpa": [
        r"\b(?:javax|jakarta)\.persistence\.",
        r"\borg\.hibernate\.",
        r"@\s*(Entity|Table|Id|GeneratedValue|Column|OneToMany|ManyToOne|OneToOne|ManyToMany|JoinColumn|PersistenceContext|Embeddable|Embedded|Transient|Lob|PrePersist|PreUpdate|PostLoad|IdClass|SequenceGenerator|NamedQuery|NamedQueries|MappedSuperclass|Basic|UniqueConstraint|GenericGenerator|Nationalized|Type)\b",
    ],
    "jdbc": [
        r"\bjava\.sql\.",
        r"\bjavax\.sql\.",
        r"jdbc:[A-Za-z0-9:_./@?=&;-]+",
        r"\bDriverManager\s*\.\s*getConnection\s*\(",
    ],
    "axis": [r"\borg\.apache\.axis2?\."],
    "jaxb": [
        r"\b(?:javax|jakarta)\.xml\.bind\.",
        r"@\s*(XmlRootElement|XmlAccessorType|XmlAccessType|XmlElement|XmlElementWrapper|XmlAttribute|XmlType|XmlTransient|XmlSchema|XmlSeeAlso)\b",
        r"\bJAXBContext\s*\.\s*newInstance\s*\(",
    ],
    "jaxws": [
        r"\b(?:javax|jakarta)\.xml\.ws\.",
        r"\bjavax\.jws\.",
        r"@\s*(WebService|WebMethod|WebParam|WebResult|WebEndpoint|WebServiceClient|WebFault|RequestWrapper|ResponseWrapper|SOAPBinding)\b",
    ],
    "jaxrs": [
        r"\b(?:javax|jakarta)\.ws\.rs\.",
        r"@\s*(Path|GET|POST|PUT|DELETE|PATCH|Produces|Consumes|PathParam|QueryParam|HeaderParam|Context)\b",
    ],
    "jasper": [r"\bnet\.sf\.jasperreports\.", r"\bJasper\w+\s*\."],
    "bouncycastle": [r"\borg\.bouncycastle\.", r"\bBouncyCastleProvider\s*\("],
    "jjwt": [r"\bio\.jsonwebtoken\.", r"\bJwts\s*\."],
    "springfox": [r"\bspringfox\.", r"@\s*EnableSwagger2\b", r"\bDocket\s*\("],
    "swagger": [r"\bio\.swagger\.", r"@\s*(Api|ApiModel|ApiModelProperty|ApiOperation|ApiParam|ApiResponse|ApiResponses)\b"],
    "xstream": [r"\bcom\.thoughtworks\.xstream\.", r"@\s*XStream\w+\b", r"\bXStream\s*\("],
    "oracle_driver": [r"\boracle\.(jdbc|sql)\.", r"jdbc:oracle:", r"\bOracle(DataSource|Driver)\b"],
    "sqlserver_driver": [r"\bcom\.microsoft\.sqlserver\.jdbc\.", r"jdbc:sqlserver:", r"\bSQLServer(DataSource|Driver)\b"],
    "lombok": [
        r"\blombok\.",
        r"@\s*(Getter|Setter|Data|Builder|SuperBuilder|NoArgsConstructor|AllArgsConstructor|RequiredArgsConstructor|EqualsAndHashCode|ToString|Slf4j)\b",
        r"@\s*ToString\s*\.\s*Exclude\b",
    ],
    "jackson": [
        r"\bcom\.fasterxml\.jackson\.",
        r"@\s*(JsonProperty|JsonIgnore|JsonInclude|JsonFormat|JsonSerialize|JsonDeserialize|JsonCreator|JsonValue)\b",
        r"\bObjectMapper\s*\(",
    ],
    "gson": [r"\bcom\.google\.gson\.", r"\bGson\s*\("],
    "logging": [r"\borg\.slf4j\.", r"\borg\.apache\.logging\.log4j\.", r"\bch\.qos\.logback\."],
    "apache_commons": [r"\borg\.apache\.commons\."],
    "servlet": [r"\b(?:javax|jakarta)\.servlet\."],
    "validation": [
        r"\b(?:javax|jakarta)\.validation\.",
        r"\borg\.hibernate\.validator\.",
        r"@\s*(NotNull|NotBlank|NotEmpty|Size|Min|Max|Email|Pattern|Valid|Validated|Length|Constraint)\b",
    ],
    "junit": [r"\borg\.junit\.", r"@\s*(Test|Before|After|BeforeEach|AfterEach|RunWith|ExtendWith)\b"],
    "mockito": [r"\borg\.mockito\.", r"@\s*(Mock|Spy|InjectMocks|Captor)\b", r"\bMockito\s*\."],
    "aspectj": [r"\borg\.aspectj\.", r"@\s*(Aspect|Around|Before|After|AfterReturning|AfterThrowing|Pointcut)\b"],
    "transaction": [r"\b(?:javax|jakarta)\.transaction\.", r"@\s*Transactional\b"],
    "apache_http": [r"\borg\.apache\.http\.", r"\bHttpClients\s*\."],
    "apache_axiom": [r"\borg\.apache\.axiom\."],
    "mail": [r"\b(?:javax|jakarta)\.mail\."],
    "crypto": [r"\bimport\s+javax\.crypto\.", r"\bCipher\s*\.\s*getInstance\s*\("],
    "itext": [r"\bcom\.itextpdf\."],
    "jfree": [r"\borg\.jfree\."],
    "firebase": [r"\bcom\.google\.firebase\.", r"\bFirebase\w+\s*\."],
    "google_auth": [r"\bcom\.google\.auth\."],
    "netty": [r"\bio\.netty\.", r"\breactor\.netty\."],
    "json": [r"\borg\.json\.", r"\bJSON(Object|Array)\s*\("],
    "thumbnailator": [r"\bnet\.coobird\.thumbnailator\."],
    "nimbus_jose": [r"\bcom\.nimbusds\.jose\.", r"\bJWEObject\s*\."],
    "jose4j": [r"\borg\.jose4j\.", r"\bJsonWebEncryption\s*\("],
    "jasypt": [r"\borg\.jasypt\.", r"\bStandardPBE\w+\s*\("],
    "jasypt_spring_boot": [r"\bcom\.ulisesbocchio\.jasyptspringboot\.", r"@\s*EnableEncryptableProperties\b"],
    "javax_annotation": [r"\b(?:javax|jakarta)\.annotation\.", r"@\s*(PostConstruct|PreDestroy|Resource)\b"],
    "jboss_logging": [r"\borg\.jboss\.logging\."],
}


COMPILED_PATTERNS = {
    family: [re.compile(pattern) for pattern in patterns]
    for family, patterns in FAMILY_PATTERNS.items()
}


FAMILY_EQUIVALENTS: dict[str, set[str]] = {
    "jpa": {"hibernate"},
}


COMMENT_RE = re.compile(r"//[^\r\n]*|/\*.*?\*/", re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit likely framework false negatives.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--subtype", default="framework")
    parser.add_argument("--query", type=Path, default=DEFAULT_QUERY)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--sample-limit", type=int, default=8)
    return parser.parse_args()


def inventory_paths(db_path: Path, source_root: Path, subtype: str) -> list[Path]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT f.absolute_path
            FROM files f
            JOIN source_roots sr ON f.source_root_id = sr.id
            WHERE sr.absolute_path = ?
              AND f.type = 'java'
              AND COALESCE(f.subtype, '') = ?
            ORDER BY f.absolute_path
            """,
            (source_root.resolve().as_posix(), subtype),
        ).fetchall()
    finally:
        conn.close()
    return [
        Path(row[0])
        for row in rows
        if "/org/apache/maven/wrapper/" not in row[0].replace("\\", "/")
    ]


def decode_text(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace"), "latin-1-replace"


def evidence_families(text: str) -> dict[str, list[str]]:
    text = COMMENT_RE.sub("", text)
    found: dict[str, list[str]] = {}
    for family, patterns in COMPILED_PATTERNS.items():
        hits: list[str] = []
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                hits.append(match.group(0)[:120])
        if hits:
            found[family] = hits
    return found


def query_capture_families(query_path: Path, source_path: Path) -> tuple[set[str], list[str], str]:
    result = subprocess.run(
        ["tree-sitter", "query", query_path.as_posix(), source_path.as_posix()],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )
    families: set[str] = set()
    captures: list[str] = []
    for line in result.stdout.splitlines():
        match = CAPTURE_RE.search(line)
        if not match:
            continue
        capture = match.group("capture")
        captures.append(capture)
        parts = capture.split(".")
        if len(parts) >= 3 and parts[0] == "framework":
            families.add(parts[1])
    stderr = result.stderr.strip()
    if result.returncode != 0 and not stderr:
        stderr = f"tree-sitter query exited {result.returncode}"
    return families, captures, stderr


def audit(paths: list[Path], query_path: Path, sample_limit: int) -> dict[str, Any]:
    start = time.time()
    evidence_counts: Counter[str] = Counter()
    captured_counts: Counter[str] = Counter()
    likely_miss_counts: Counter[str] = Counter()
    encodings: Counter[str] = Counter()
    samples: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    query_failures: list[dict[str, str]] = []
    files_with_evidence = 0
    files_with_likely_miss = 0

    for index, path in enumerate(paths, 1):
        text, encoding = decode_text(path)
        encodings[encoding] += 1
        evidence = evidence_families(text)
        if evidence:
            files_with_evidence += 1
        captured_families, captures, query_error = query_capture_families(query_path, path)
        if query_error:
            query_failures.append({"path": path.as_posix(), "error": query_error})

        for family in evidence:
            evidence_counts[family] += 1
        for family in captured_families:
            captured_counts[family] += 1

        missed = []
        for family in sorted(evidence):
            equivalent_captures = FAMILY_EQUIVALENTS.get(family, set())
            if family not in captured_families and not (equivalent_captures & captured_families):
                missed.append(family)
        if missed:
            files_with_likely_miss += 1
        for family in missed:
            likely_miss_counts[family] += 1
            if len(samples[family]) < sample_limit:
                samples[family].append(
                    {
                        "path": path.as_posix(),
                        "evidence": evidence[family],
                        "captured_families": sorted(captured_families),
                        "capture_count": len(captures),
                    }
                )

        if index % 500 == 0:
            print(f"progress {index}/{len(paths)} elapsed={time.time() - start:.1f}s", flush=True)

    family_rows = []
    for family in sorted(FAMILY_PATTERNS):
        family_rows.append(
            {
                "family": family,
                "files_with_text_evidence": evidence_counts[family],
                "files_with_query_capture": captured_counts[family],
                "likely_miss_files": likely_miss_counts[family],
                "samples": samples[family],
            }
        )

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "grammar_root": ROOT.as_posix(),
        "query": query_path.as_posix(),
        "inventory_files": len(paths),
        "files_with_text_evidence": files_with_evidence,
        "files_with_likely_miss": files_with_likely_miss,
        "query_failures": query_failures,
        "encoding_counts": dict(sorted(encodings.items())),
        "elapsed_seconds": round(time.time() - start, 2),
        "families": family_rows,
    }


def write_report(report_path: Path, result: dict[str, Any]) -> None:
    rows = result["families"]
    assert isinstance(rows, list)
    failures = result["query_failures"]
    assert isinstance(failures, list)

    lines = [
        "# Framework False Negative Audit",
        "",
        f"Date: {result['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Inventory files: {result['inventory_files']}",
        f"- Files with text evidence: {result['files_with_text_evidence']}",
        f"- Files with likely family misses: {result['files_with_likely_miss']}",
        f"- Query failures: {len(failures)}",
        f"- Elapsed seconds: {result['elapsed_seconds']}",
        "",
        "## Encodings",
        "",
        "| Encoding | Files |",
        "| --- | ---: |",
    ]
    for encoding, count in result["encoding_counts"].items():
        lines.append(f"| `{encoding}` | {count} |")

    lines.extend(
        [
            "",
            "## Family Coverage",
            "",
            "| Family | Text Evidence Files | Query Capture Files | Likely Miss Files |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in sorted(rows, key=lambda item: (-item["likely_miss_files"], item["family"])):
        lines.append(
            f"| `{row['family']}` | {row['files_with_text_evidence']} | "
            f"{row['files_with_query_capture']} | {row['likely_miss_files']} |"
        )

    lines.extend(["", "## Likely Miss Samples", ""])
    for row in sorted(rows, key=lambda item: (-item["likely_miss_files"], item["family"])):
        if not row["likely_miss_files"]:
            continue
        lines.extend([f"### `{row['family']}`", ""])
        for sample in row["samples"]:
            evidence = ", ".join(f"`{item}`" for item in sample["evidence"])
            captured = ", ".join(f"`{item}`" for item in sample["captured_families"]) or "none"
            lines.append(f"- Path: `{sample['path']}`")
            lines.append(f"  Evidence: {evidence}")
            lines.append(f"  Captured families: {captured}")
        lines.append("")

    if failures:
        lines.extend(["## Query Failures", ""])
        for failure in failures[:20]:
            lines.append(f"- `{failure['path']}`: `{failure['error']}`")
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "Likely misses are conservative text-evidence hits whose framework family was not captured by `queries/frameworks.scm` in the same file.",
            "They are review candidates, not automatic grammar failures. A miss should become a grammar rule only when the syntax is local, stable, and cannot collide with ordinary Java identifiers.",
        ]
    )
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    paths = inventory_paths(args.db, args.source_root, args.subtype)
    result = audit(paths, args.query.resolve(), args.sample_limit)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_report(args.report_out, result)
    print(f"inventory_files          : {result['inventory_files']}")
    print(f"files_with_text_evidence : {result['files_with_text_evidence']}")
    print(f"files_with_likely_miss   : {result['files_with_likely_miss']}")
    print(f"query_failures           : {len(result['query_failures'])}")
    print(f"json_out                 : {args.json_out}")
    print(f"report_out               : {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
