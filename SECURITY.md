# Security policy

## Supported versions

The project is in active development (0.x). Only the latest published
version from the `main` branch receives security fixes.

| Version | Supported           |
| ------- | -------------------- |
| 0.1.x   | :white_check_mark:  |
| < 0.1   | :x:                  |

## Reporting a vulnerability

`ofi-chain-forensics` is an analysis library that works exclusively on
local data explicitly provided by the user (JSON/CSV files) — it makes
no network requests and does not connect to any live blockchain. The
attack surface is therefore limited mainly to:

- Parsing of input data (transaction JSON, blacklist files) that could
  trigger unexpected behavior (e.g. denial-of-service via malformed
  input, infinite loops).
- External dependencies (`networkx`) with known vulnerabilities.

If you find a security vulnerability (not a regular functional bug —
for those, open a normal issue), please:

1. **Do not open a public issue** with exploitation details.
2. Contact the maintainer (Ciprian-LocalPulse) directly through the
   channels listed on the GitHub profile, or open a private issue
   tagged `security` without technical details, requesting a private
   communication channel.
3. Include: description of the issue, reproduction steps, estimated
   impact.

You will receive an acknowledgment within a reasonable time, and the
issue will be handled with priority. If the vulnerability is confirmed,
a fix will be published and, if applicable, an advisory, with credit
for the report (if you wish).
