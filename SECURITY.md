# Security Policy

## Reporting a vulnerability

Please do not report security vulnerabilities in public GitHub issues.

Use GitHub's private vulnerability reporting for this repository, or contact the repository maintainer privately through GitHub. Include the affected version or commit, reproduction steps, impact, and any suggested mitigation. Do not include live API keys or other secrets in a report.

## Supported versions

Security fixes are currently provided for the latest version on the default branch. This project is pre-1.0, so compatibility and support guarantees may change.

## Operational guidance

- Keep `.env` out of version control.
- Never paste provider tokens into issues, pull requests, logs, or LangSmith metadata.
- Do not deploy the local `memory.json` persistence or unauthenticated API publicly.
