# Security policy

## Supported versions

Security fixes target the latest tagged release.

| Version | Supported |
| --- | --- |
| 1.3.x | Yes |
| 1.2.0-alpha.x and earlier | No |

## Report a vulnerability

Report vulnerabilities through GitHub private vulnerability reporting for this repository. If it is unavailable, contact the repository owner privately through their GitHub profile and include “Littlepowers security report” in the subject or first line.

Do not open a public issue for a suspected vulnerability. Do not include real credentials, private source code, harmful payloads, or data from systems you do not own.

Include:

- affected version and host;
- operating system and Python version;
- exact preconditions;
- minimal reproduction in a disposable repository;
- expected and observed behavior;
- impact and suggested mitigation, if known.

The maintainer will acknowledge a complete report within seven days and provide a remediation or status update within 30 days. These are response targets, not disclosure deadlines. Coordinate public disclosure after a fix is available.

## Scope

High-priority reports include:

- writes outside the selected workspace;
- state or Hook prompt injection that crosses the documented data boundary;
- unexpected network or transcript access;
- lost-update or archive failures that bypass workflow revision checks;
- Review Gate, exact-resolution, runner-claim, or Project Workflow Index trust-boundary bypasses;
- plugin installation or Hook command injection;
- bypasses of tracked-file, symlink, size, or artifact-path validation.

Model non-compliance with a documented best-effort reminder is not by itself a security vulnerability. See the [security model](docs/security-model.md) for assumptions and residual risks.
