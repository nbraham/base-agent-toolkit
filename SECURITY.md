# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it responsibly.

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to Report

1. Email: [security contact TBD]
2. Include: description, reproduction steps, and impact assessment

### What We Consider Security Issues

- Private key exposure or leakage
- Transaction manipulation
- Signature forgery
- Unauthorized fund movement
- x402 payment bypass
- Keystore encryption weaknesses

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Security Best Practices

See [Security Guide](docs/guides/security.md) for detailed best practices.

### Quick Checklist

- [ ] Private keys stored in env vars or encrypted keystore
- [ ] Daily budget limits configured
- [ ] Transaction value guards enabled
- [ ] Dry-run mode tested before live deployment
- [ ] Token approvals set to exact amounts
- [ ] x402 payment limits configured
