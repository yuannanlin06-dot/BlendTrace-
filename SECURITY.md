# Security Policy

## Supported version

The current prototype is v0.1.1.

## Reporting a security issue

Please open a GitHub issue that describes the behavior without posting real credentials, private files, API keys or other sensitive personal data.

## Publisher checklist

Before publishing a modified release:

1. Search the repository for API keys, tokens, passwords, private URLs and local absolute paths.
2. Do not commit `.blend` project files unless they are intentionally public examples.
3. Do not commit environment files, credentials, caches or editor-specific private settings.
4. Review every new dependency and every new network or file-system permission.
5. Treat any credential accidentally committed to Git history as exposed and revoke/rotate it; deleting the visible line alone is not sufficient.
