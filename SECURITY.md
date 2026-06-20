# Security Policy

## Supported Versions

FastParse is currently preparing its first public preview.

Security fixes should target the latest published release and the main development branch.

## Reporting A Vulnerability

Please report security issues privately through GitHub security advisories when available.

If advisories are not enabled yet, open a minimal issue asking for a private contact path without posting exploit details.

## Scope

Security-relevant areas include:

- Native memory safety.
- Parser crashes caused by malformed source bytes.
- Incorrect native result ownership.
- Binary MessagePack decoder issues in bindings.
- Build or packaging scripts that could execute unexpected code.

FastParse does not intentionally perform file I/O, network I/O, database writes, or process execution in the native core.
