# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: security@ironrep.com

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, XSS, etc.)
- Full paths of source file(s) related to the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

## Security Measures

IronRep implements the following security measures:

### Authentication & Authorization
- Session-based token storage (sessionStorage)
- JWT tokens with expiration
- Automatic token cleanup on session end
- 401/403 automatic redirect to login

### Data Protection
- Input validation on all forms
- TypeScript strict mode for type safety
- Sanitized user inputs
- HTTPS enforcement (production)

### API Security
- Automatic retry with exponential backoff
- Request/response interceptors
- Error classification and handling
- Rate limiting (server-side)

### Frontend Security
- No inline scripts
- Content Security Policy headers
- XSS protection via React's built-in escaping
- Secure cookie settings

### Code Quality
- Centralized logging
- Error boundaries
- Type-safe interfaces (100% TypeScript)
- Automated testing

## Bug Bounty Program

Currently, we do not have a formal bug bounty program. However, we appreciate responsible disclosure and will acknowledge security researchers in our release notes (with permission).

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release patches as soon as possible

## Comments

We take security seriously and appreciate your efforts to responsibly disclose findings.
